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

    manga_downloader = BatotoDownloader(dl_dir)

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--series", type=str, help="Bato.to Series URL. Downloads entire series.", required=False)
        parser.add_argument("-c", "--chapter", type=str, help="Bato.to Chapter URL. Downloads only specified chapter.", required=False)
        args = parser.parse_args()

        if args.series is not None:
            manga_downloader.download(series_url=args.series)
        elif args.chapter is not None:
            manga_downloader.download(chapter_url=args.chapter)
        else:
            print("Please provide at least one argument. Run `python main.py -h` if you need help.`")
    except Exception as e:
        main_logger.exception(e)
        print("Error, please check the log.")


if __name__ == "__main__":
    main()
