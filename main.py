from collections import OrderedDict
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image
import requests
from requests_html import HTMLSession


def get_chapter_links(chapter_base_url: str, soup: BeautifulSoup) -> dict[str, str]:
    '''
    Retrieves the list of chapter URLs from Bato.to for the provided series.
    Returns a dictionary with the chapter number as key and the URL as value.
    '''

    chapter_links = OrderedDict()
    for chapter in soup.find_all("a", class_="visited chapt", href=True):
        chapter_no_element = chapter.find("b")
        chapter_no = chapter_no_element.text.split(" ")[1]
        chapter_link = chapter["href"]
        chapter_links[chapter_no] = f"{chapter_base_url}{chapter_link}"
        ordered_chapter_links = OrderedDict(reversed(chapter_links.items()))
    return ordered_chapter_links


def determine_page_number(page_link: str) -> int:
    '''Determines and returns the total number of pages for the specified chapter.'''

    tmp_page_link = page_link + "/1"
    page_no_page = requests.get(tmp_page_link)
    no_soup = BeautifulSoup(page_no_page.content, "html.parser")
    no_list = no_soup.find("optgroup", label="Page")
    pages = int(no_list.find("option").text.split("/")[1])

    return pages


def get_image(page: int, chapter_link: str) -> Image:
    '''
    Retrieves the raw image from the specified page URL and
    returns an Image object based on the retrieved data.
    '''

    page_link = chapter_link + f"/{page}"

    with HTMLSession() as session:
        chapter_page = session.get(page_link)
        chapter_page.html.render()

        element = chapter_page.html.find(".page-img")
        source = element[0].attrs["src"]

    image = Image.open(requests.get(source, stream=True).raw)

    return image

def download_manga(chapter, chapter_link, title, cur_dir):
    filedir = (cur_dir / f"Manga/{title}/{chapter}")
    try:
        filedir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Chapter \"{chapter}\" directory exists, skipping download...")
        return

    pages = determine_page_number(chapter_link)

    if pages > 99:
        chapter_length = 3
    elif pages > 9:
        chapter_length = 2
    else:
        chapter_length = 1

    for page in range(1, pages + 1):
        image = get_image(page, chapter_link)

        file = filedir / f"{page:0{chapter_length}}.jpg"
        image.save(file)
        print(f"Completed {page}/{pages} of Chapter {chapter}.")
    return


def main():
    '''Main function.'''

    cur_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()

    SERIES_URL = input("Please provide the Manga series bato.to URL: ")
    CHAPTER_BASE_URL = "https://bato.to"

    response = requests.get(SERIES_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("title").text.replace(" Manga", "")
    chapter_links = get_chapter_links(CHAPTER_BASE_URL, soup)
    valid_choices = [0, len(chapter_links)]
    print(f"Manga: {title}\nTotal chapters: {len(chapter_links)}")
    text = "[0] Download all"
    for i in range(len(list(chapter_links.items()))):
        text += f"\n[{i+1}] {list(chapter_links.items())[i][0]}"
    print(text)
    choice_invalid = True
    while choice_invalid:
       try:
           choice = int(input("Please enter the number of your choice: "))
           if choice <= len(chapter_links) and choice >= 0:
               choice_invalid = False
           else:
               print(f"Make sure your choice is between 0 and {len(chapter_links)}!")
       except Exception as e:
           print(f"Make sure your choice is between 0 and {len(chapter_links)}!\n{e}")



    for chapter, chapter_link in chapter_links.items():
        if choice == 0:
            download_manga(chapter, chapter_link, title, cur_dir)
        else:
            if str(chapter) == list(chapter_links.items())[choice-1][0]:
                download_manga(chapter, chapter_link, title, cur_dir)
    if choice == 0:
        print("All chapters have finished downloading!")


if __name__ == "__main__":
    main()
