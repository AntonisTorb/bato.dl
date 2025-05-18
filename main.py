import argparse
import logging
from pathlib import Path
from batodl import BatotoDownloader


def main():
    '''Main function.'''

    cwd: Path = Path.cwd()

    dl_dir = Path.cwd() / "Manga"
    dl_dir.mkdir(exist_ok=True)

    log_path = cwd / "batodl.log"
    main_logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(filename=log_path.name, 
                        level=logging.INFO,
                        format="%(asctime)s|%(levelname)8s|%(name)s|%(message)s")

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--series", type=str, help="Bato.to Series URL. Downloads entire series.", required=False)
        parser.add_argument("-sc", "--starting_chapter", type=str, help="Start downloading from specified chapter ignoring previous ones.", required=False)
        parser.add_argument("-ec", "--ending_chapter", type=str, help="Finish downloading at specified chapter ignoring following ones.", required=False)
        parser.add_argument("-c", "--chapter", type=str, help="Bato.to Chapter URL. Downloads only specified chapter.", required=False)
        parser.add_argument("-d", "--daiz", action="store_true", help="Enforce daiz naming scheme.", required=False)
        parser.add_argument("-e", "--extension", type=str, help="Image type extension. If not specified, the original will be used", required=False)
        parser.add_argument("-rt", "--raw_title", action="store_true", help="Use the raw title as the chapter directory name, ignoring all formating", required=False)

        args = parser.parse_args()

        chapter_name_format = "default"
        if args.daiz:
            chapter_name_format = "daiz"
        elif args.raw_title:
            chapter_name_format = "raw"

        manga_downloader = BatotoDownloader(dl_dir, chapter_name_format, args.extension)

        if args.series is not None:
            starting_chapter = args.starting_chapter
            ending_chapter = args.ending_chapter
            manga_downloader.download(series_url=args.series, starting_chapter = starting_chapter, ending_chapter = ending_chapter)
        elif args.chapter is not None:
            manga_downloader.download(chapter_url=args.chapter, starting_chapter = None, ending_chapter = None)
        else:
            print("Please provide at least one argument. Run `python main.py -h` if you need help.`")
    except Exception as e:
        main_logger.exception(e)
        print("Error, please check the log.")


if __name__ == "__main__":
    main()
