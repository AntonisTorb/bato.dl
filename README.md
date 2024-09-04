# bato.dl
Script to download manga chapters from bato.to. Compatible with both v3x and v2x.

## How to use
- Install the required packages with the command: `pip install -r requirements.txt`
- Run the script with the command `python main.py` and by providing one of the following command line arguments:

    - `-s "series url"` or `--series "series url"`: Bato.to Series URL. Downloads entire series.
    - `-c "chapter url"` or `--chapter "chapter url"`: Bato.to Chapter URL. Downloads only specified chapter.

    *Example 1:* `python main.py -c "chapter url goes here"`
    
    *Example 2:* `python main.py -s "series url goes here"`

- **Optional:** If you want to enforce a [Daiz-like naming scheme](https://github.com/Daiz/manga-naming-scheme), please also add the `-d` command line argument.

    *Example 3:* `python main.py -c "chapter url goes here" -d`

    *Example 4:* `python main.py -s "series url goes here" -d`

- **Optional:** After the download is finished you may run `python mangaconverter.py` to convert the manga images into a single pdf-file each chapter. (Don't forget to edit your folder path in line 7)

## Contributions
Thank you everyone below for improving this project!

- [hoemotion](https://github.com/AntonisTorb/bato.dl/pull/1)
- [Cleanup-Crew-From-Discord](https://github.com/AntonisTorb/bato.dl/pull/2)
- [Emylou-s](https://github.com/AntonisTorb/bato.dl/pull/3)

## Thank you and enjoy :)
