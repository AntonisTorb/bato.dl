# bato.dl
Script to download manga chapters from bato.to. Compatible with both v3x and v2x.

## How to use
- Install the required packages with the command: `pip install -r requirements.txt`
- Run the script with the command `python main.py` and by providing one of the following command line arguments:

    - `-s "series url"` or `--series "series url"`: Bato.to Series URL. Downloads entire series.
    - `-c "chapter url"` or `--chapter "chapter url"`: Bato.to Chapter URL. Downloads only specified chapter.

    *Example 1:* `python main.py -c "chapter url goes here"`
    
    *Example 2:* `python main.py -s "series url goes here"`

    If you want to download only some chapters of a series, you can use the `-sc` and `-ec` to specify the starting chapter and ending chapter:
    - `-s "series url" -sc "starting chapter number" -ec "ending chapter number"`

    *Example 3:* `python main.py -s "series url goes here" -sc 5 -ec 15.5`

- **Optional:** If you want to enforce a [Daiz-like naming scheme](https://github.com/Daiz/manga-naming-scheme), please also add the `-d` command line argument. If you want to have the raw chapter title as the chapter directory name, please add the `-rt` command line argument (only for series, mostly useful for those that have an unconventional chapter naming convension that causes issues).

    *Example 4:* `python main.py -c "chapter url goes here" -d`

    *Example 5:* `python main.py -s "series url goes here" -rt`

- **Optional:** You can choose your own file extension for the resulting images by specifying it with the `-e` argument (please refer to the [Pillow Documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) for a the acceptable file formats). If not specified, the original file extension will be used.

    *Example 6:* `python main.py -c "chapter url goes here" -e 'jpg'`

    *Example 7:* `python main.py -s "series url goes here" -d -e 'png'`

- **Optional:** After the download is finished you may run `python mangaconverter.py` to convert the manga images into a single pdf-file each chapter. (Don't forget to edit your folder path in line 7)

## Contributions
Thank you everyone below for improving this project!

- [hoemotion](https://github.com/AntonisTorb/bato.dl/pull/1)
- [Cleanup-Crew-From-Discord](https://github.com/AntonisTorb/bato.dl/pull/2)
- [Emylou-s](https://github.com/AntonisTorb/bato.dl/pull/3)
- [Godangel ](https://github.com/AntonisTorb/bato.dl/pull/6)

## Thank you and enjoy :)
