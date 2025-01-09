from collections import OrderedDict
from io import BytesIO
import json
from math import log10
import logging
from pathlib import Path
import re
import sys
import time

from bs4 import BeautifulSoup, Tag
from PIL import Image
import requests


class BatotoDownloader():

    def __init__(self, dl_dir: Path, daiz: bool, extension:str|None) -> None:
        '''Downloader Class for Bato.to manga.'''

        self.dl_dir = dl_dir
        self.daiz = daiz
        self.extension = extension

        self.logger: logging.Logger = logging.getLogger(__name__)
        self.chapter_base_url: str = "https://bato.to"
        self.headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
        }


    def get_chapter_urls(self, soup: BeautifulSoup) -> OrderedDict[str, str]:
        '''
        Retrieves the list of chapter URLs from Bato.to for the provided series.
        Returns a dictionary with the chapter number as key and the URL as value.
        '''

        web_version: int = 3
        chapter_urls = OrderedDict()
        chapter_list = soup.find_all("a", class_="visited:text-accent", href=True)
        if not chapter_list:
            web_version = 2
            chapter_list: list[Tag] = soup.find_all("a", class_="visited chapt", href=True)
        for chapter in chapter_list:
            if web_version == 3:
                chapter_no = chapter.text.split(" ")[-1]
            elif web_version == 2:
                chapter_no_element: Tag = chapter.find("b")
                chapter_no = chapter_no_element.text.split(" ")[-1]

            chapter_url = chapter["href"]
            chapter_urls[chapter_no] = f"{self.chapter_base_url}{chapter_url}"

            if web_version == 3:
                ordered_chapter_urls = OrderedDict(chapter_urls.items())
            elif web_version == 2:
                ordered_chapter_urls = OrderedDict(reversed(chapter_urls.items()))

        return ordered_chapter_urls


    def download_chapter(self, chapter_no: str, chapter_url: str, title: str, session: requests.Session) -> None:
        '''Downloads a chapter from the provided URL and saves it.'''

        web_version: int = 3
        manga_dir = self.dl_dir / title.strip()
        manga_dir.mkdir(exist_ok=True)

        if self.daiz:
            try:
                if "." in str(chapter_no):
                    decimals = len(chapter_no.split(".")[-1])
                    whole_len = 4 + decimals
                    chapter_no = f'{float(chapter_no):0{whole_len}.{decimals}f}'
                else:
                    chapter_no = f'{int(chapter_no):03}'
            except ValueError: # Error when last part of chapter name is not a number (like "Finale")
                pass

            chapter_dir: Path = manga_dir / f'{title} - {chapter_no}'

        else:
            chapter_dir: Path = manga_dir / chapter_no

        existing_pages: list[str|int] = []
        if chapter_dir.exists():
            # List of existing pages without file extension.
            if self.daiz:
                existing_pages = [item.stem for item in chapter_dir.glob("*.*")]
            else:
                try:
                    for item in chapter_dir.glob("*.*"):
                        existing_pages.append(int(item.stem))
                except ValueError:  # If irrelevant file somehow in chapter directory.
                    pass
        else:
            chapter_dir.mkdir(exist_ok=True)
        
        r: requests.Response = session.get(chapter_url, headers=self.headers, timeout=5)
        if r.status_code != 200:
            self.logger.error(f'Error getting chapter {chapter_no} html page: Response status code: {r.status_code}')
            sys.exit(0)

        reg: re.Pattern = re.compile(r"\[\[0,\\&quot;https:.*.(webp|jpg|jpeg|png)\\&quot;\]\]")
        links_match: re.Match | None = re.search(reg, r.text)
        if links_match is None:
            web_version = 2

        if web_version == 3:
            links_res: str = links_match.string[links_match.start():links_match.end()]
            urls_str: str = links_res.replace(r"\&quot;", "\"")
            urls_list = json.loads(urls_str)
            page_urls = [sublist[1] for sublist in urls_list]
        elif web_version == 2:
            reg: re.Pattern = re.compile("const imgHttps = (.*);\n")
            page_urls: list[str] = json.loads(*re.findall(reg, r.text))
        
        if len(existing_pages) == len(page_urls):
            return
        
        for page_no, url in enumerate(page_urls[len(existing_pages):], start=len(existing_pages)):
            retries: int = 5
            while retries:
                try:
                    print(f'Getting Chapter {chapter_no}, page {page_no+1}...{" "*10}', end="\r")
                    r: requests.Response = session.get(url, headers=self.headers, timeout=5)
                    if r.status_code == 200:
                        break
                    print(f'Error for Chapter {chapter_no}, Page {page_no}, retrying...')
                    retries -= 1
                except Exception as e:
                    print(f'Error for Chapter {chapter_no}, Page {page_no}, retrying...')
                    self.logger.exception(e)
                    retries -= 1
                time.sleep(2)
            
            if not retries or r.status_code != 200:
                if r.status_code != 200:
                    self.logger.error(f'Error for Chapter {chapter_no}, Page {page_no+1}: Response status code: {r.status_code}')
                print(f'Error getting page {page_no+1} of chapter {chapter_no}. Please check the log. Exiting...')
                sys.exit(0)

            if self.daiz:
                if self.extension is None:
                    img_path: Path = chapter_dir / f'{title} - {chapter_no} - {page_no+1:03}.{url.split(".")[-1]}'
                else:
                    img_path: Path = chapter_dir / f'{title} - {chapter_no} - {page_no+1:03}.{self.extension}'
            else:
                page_format: int = 1 + int(log10(len(page_urls)))  # How many leading zeros in page file name.
                if self.extension is None:
                    img_path: Path = chapter_dir / f'{page_no+1:0{page_format}}.{url.split(".")[-1]}'
                else:
                    img_path: Path = chapter_dir / f'{page_no+1:0{page_format}}.{self.extension}'

            if self.extension is None or url.split(".")[-1] == self.extension:
                with open(img_path, "wb") as f:
                    f.write(BytesIO(r.content).getbuffer())
                    continue
            img: Image.Image = Image.open(BytesIO(r.content))
            img.save(img_path)


    def download_manga(self, chapter_urls: OrderedDict[str, str], title: str, session: requests.Session) -> None:
        '''Downloads all the chapters in the series from the provided URL and saves them.'''

        manga_dir: Path = self.dl_dir / title

        existing_chapters: list[str] = []
        if manga_dir.exists():
            existing_chapters = [item.name.split("-")[-1].strip() for item in manga_dir.iterdir() if item.is_dir()]
        else:
            manga_dir.mkdir(exist_ok=True)

        last = []
        for chapter_no, chapter_url in chapter_urls.items():
            existing_chapters_float: list[float] = []
            for chapter in existing_chapters:
                try:
                    existing_chapters_float.append(float(chapter))
                except ValueError:  # If irrelevant directory somehow in series directory.
                    pass
            
            try:
                if float(chapter_no) in existing_chapters_float:
                    last = [chapter_no, chapter_url]
                    continue
            except ValueError: # Error when last part of chapter name is not a number (like "Finale")
                continue

            if last:  # Check last for missing pages.
                self.download_chapter(last[0], last[1], title, session)
                last = []

            self.download_chapter(chapter_no, chapter_url, title, session)
            

    def download(self, *, series_url: str = "", chapter_url: str = "") -> None:
        '''Download manager to determine the steps required to get entire series or single chapter.'''

        try:
            session = requests.Session()

            special_reg = re.compile(r'(\\|\/|\:|\*|\?|\"|\<|\>|\||)')
            if series_url:
                r: requests.Response = session.get(series_url, headers=self.headers, timeout=5)
                if r.status_code != 200:
                    self.logger.error(f'Error getting series html page: Response status code: {r.status_code}')
                    sys.exit(0)

                soup = BeautifulSoup(r.content, "html.parser")

                title: str = soup.find("title").text.replace(" Manga", "").replace(" - Read Free Online at Bato.To", "")
                title = re.sub(special_reg, "", title)
                chapter_urls: OrderedDict[str, str] = self.get_chapter_urls(soup)

                self.download_manga(chapter_urls, title, session)
            elif chapter_url:
                r: requests.Response = session.get(chapter_url, headers=self.headers, timeout=5)
                if r.status_code != 200:
                    self.logger.error(f'Error getting chapter html page: Response status code: {r.status_code}')
                    sys.exit(0)

                soup = BeautifulSoup(r.content, "html.parser")

                html_title = soup.find("title").text.replace(" - Read Free Manga Online at Bato.To", "")
                title_re: re.Pattern = re.compile(r"(.*)-[^1-9]*([0-9\.]*)")
                title, chapter_no = re.findall(title_re, html_title)[0]
                title = title.strip()
                title = re.sub(special_reg, "", title)
                
                self.download_chapter(chapter_no, chapter_url, title, session) 
            else:
                return
            
            print(f'Downloads finished!{" "*20}')

        except Exception as e:
            self.logger.exception(e)
            print(f'Error, please check the log.{" "*20}')
            sys.exit(0)
