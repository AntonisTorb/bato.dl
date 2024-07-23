# bato.dl
Script to download manga chapters from bato.to.

## How to use
- Install the required packages with the command: `pip install -r requirements.txt`
- Run the script with the command `python main.py` and by providing one of the following command line arguments:

    - `-s "series url"` or `--series "series url"`: Bato.to Series URL. Downloads entire series.
    - `-c "series url"`, `--chapter "series url"`: Bato.to Chapter URL. Downloads only specified chapter.

    *Example:* `python main.py -c "chapter url goes here"`
- **Optional:** After the download is finished you may run `python mangaconverter.py` to convert the manga images into a single pdf-file each chapter. (Don't forget to edit your folder path in line 7)

## Contributions
Thank you everyone below for improving this project!

- [hoemotion](https://github.com/AntonisTorb/bato.dl/pull/1)
- [Cleanup-Crew-From-Discord](https://github.com/AntonisTorb/bato.dl/pull/2)
- [Emylou-s](https://github.com/AntonisTorb/bato.dl/pull/3)

## Thank you and enjoy :)
