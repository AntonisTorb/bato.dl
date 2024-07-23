from collections import OrderedDict
from io import BytesIO
import json
from math import log10
import logging
from pathlib import Path
import re
import sys
import time

from bs4 import BeautifulSoup
from PIL import Image
import requests


class BatotoDownloader():

    def __init__(self, dl_dir: Path) -> None:
        '''Downloader Class for Bato.to manga.'''

        self.dl_dir = dl_dir

        self.logger: logging.Logger = logging.getLogger(__name__)
        self.chapter_base_url = "https://bato.to"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
        }


    def get_chapter_urls(self, soup: BeautifulSoup) -> OrderedDict[str, str]:
        '''
        Retrieves the list of chapter URLs from Bato.to for the provided series.
        Returns a dictionary with the chapter number as key and the URL as value.
        '''

        chapter_urls = OrderedDict()
        for chapter in soup.find_all("a", class_="visited chapt", href=True):
            chapter_no_element = chapter.find("b")
            chapter_no = chapter_no_element.text.split(" ")[-1]
            chapter_url = chapter["href"]
            chapter_urls[chapter_no] = f"{self.chapter_base_url}{chapter_url}"
            ordered_chapter_urls = OrderedDict(reversed(chapter_urls.items()))
        return ordered_chapter_urls


    def download_chapter(self, chapter_no: str, chapter_url: str, manga_dir: Path, session: requests.Session) -> None:
        '''Downloads a chapter from the provided URL and saves it.'''

        chapter_dir: Path = manga_dir / chapter_no

        existing_pages = []
        if chapter_dir.exists():
            # List of existing pages without file extension.
            existing_pages = [int(item.stem) for item in chapter_dir.glob("*.jpg")]
        else:
            chapter_dir.mkdir(exist_ok=True)
        
        r: requests.Response = session.get(chapter_url, headers=self.headers, timeout=5)
        if r.status_code != 200:
            self.logger.error(f'Error getting chapter {chapter_no} html page: Response status code: {r.status_code}')
            sys.exit(0)

        reg: re.Pattern = re.compile("const imgHttps = (.*);\n")
        page_urls: list[str] = json.loads(*re.findall(reg, r.text))

        if len(existing_pages) == len(page_urls):
            return
        
        page_format: int = 1 + int(log10(len(page_urls)))  # How many leading zeros in page file name.

        for page_no, url in enumerate(page_urls):
            if page_no + 1 in existing_pages:
                continue

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
                    self.logger.error(f'Error for Chapter {chapter_no}, Page {page_no}: Response status code: {r.status_code}')
                print("Error getting page {page_no} of chapter {chapter_no}. Please check the log. Exiting...")
                sys.exit(0)

            img: Image.Image = Image.open(BytesIO(r.content))
            img_path: Path = chapter_dir / f'{page_no+1:0{page_format}}.jpg'
            img.save(img_path)


    def download_manga(self, chapter_urls: OrderedDict[str, str], title: str, session: requests.Session) -> None:
        '''Downloads all the chapters in the series from the provided URL and saves them.'''

        manga_dir: Path = self.dl_dir / title

        existing_chapters: list[str] = []
        if manga_dir.exists():
            existing_chapters = [item.name for item in manga_dir.iterdir() if item.is_dir()]
        else:
            manga_dir.mkdir(exist_ok=True)

        last = []
        for chapter_no, chapter_url in chapter_urls.items():
            if chapter_no in existing_chapters:
                last = [chapter_no, chapter_url]
                continue
            if last:  # Check last for missing pages.
                self.download_chapter(last[0], last[1], manga_dir, session)
                last = []

            self.download_chapter(chapter_no, chapter_url, manga_dir, session)
            

    def download(self, *, series_url: str = "", chapter_url: str = "") -> None:
        '''Download manager to determine the steps required to get entire series or single chapter.'''

        try:
            session = requests.Session()

            if series_url:
                r: requests.Response = session.get(series_url, headers=self.headers, timeout=5)
                if r.status_code != 200:
                    self.logger.error(f'Error getting series html page: Response status code: {r.status_code}')
                    sys.exit(0)

                soup = BeautifulSoup(r.content, "html.parser")

                title: str = soup.find("title").text.replace(" Manga", "")
                chapter_urls: OrderedDict[str, str] = self.get_chapter_urls(soup)

                self.download_manga(chapter_urls, title, session)
            elif chapter_url:
                r: requests.Response = session.get(chapter_url, headers=self.headers, timeout=5)
                if r.status_code != 200:
                    self.logger.error(f'Error getting chapter html page: Response status code: {r.status_code}')
                    sys.exit(0)

                soup = BeautifulSoup(r.content, "html.parser")

                html_title = soup.find("title").text

                title_re: re.Pattern = re.compile("(.*) - Chapter ([0-9]*)")
                title, chapter_no = re.findall(title_re, html_title)[0]
                manga_dir = self.dl_dir / title.strip()
                manga_dir.mkdir(exist_ok=True)

                self.download_chapter(chapter_no, chapter_url, manga_dir, session) 
            else:
                return
            
            print(f'Downloads finished!{" "*20}')

        except Exception as e:
            self.logger.exception(e)
            print(f'Error, please check the log.{" "*20}')
            sys.exit(0)
