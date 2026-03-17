# STSongSearcher
Ever looked at a Discogs release and gone "damn, I wonder how many of these songs are completely unknown to the internet"? Well, now you can start to find out, if you want.

This program grabs the tracklist of a Discogs release, then searches each song on Spotify, Bandcamp, and YouTube, logging the results in a text file. It can either get a random release from a search page (with all the usual Discogs filters, like filtering to a specific artist, barcode, or searching for a specific track name) or you can enter a release ID (Master Release or a normal release).

## Shameless self-promotion
If you're looking at this of your own volition, you're probably at least a little interested in obscure media. If yes, then take a look at **[Destruction Media Archive](https://www.youtube.com/@destructionmediaarchive)** :]

## Requirements
This program is confirmed to work in Python 3.14.3. Any other versions may or may not work.

### Packages
* [`python3-discogs-client`](https://pypi.org/project/python3-discogs-client/)
* [`spotify_client`](https://pypi.org/project/spotify-client/)
* [`py-bandcamp`](https://pypi.org/project/py-bandcamp/)
* [`youtube-search`](https://pypi.org/project/youtube-search/)

Also `os`, `sys`, `json`, `traceback`, `time`, and `random`, if you somehow installed Python without installing those.

### Other
You will need API keys:
* [Discogs personal access token](https://www.discogs.com/settings/developers)
* Spotify client ID and secret key ([instructions here](https://developer.spotify.com/documentation/web-api/concepts/apps) - Redirect URI doesn't matter, set it to `http://127.0.0.1:3000` or something like that; the only checkbox you need is Web API).

I don't really want to implement OAuth, so this is the next best option.

## How to use
1. Install all required packages, and obtain your API keys.
2. Download `STSongSearcher.py`.
3. Open `STSongSearcher.py` with an IDE or text editor.
4. Replace the placeholder values for the variables `SPOTIFY_CLIENT_ID`, `SPOTIFY_SECRET_KEY`, and `DISCOGS_TOKEN` with their respective keys. Save the file.
5. Run `STSongSearcher.py` and follow the instructions.

The program will create a new folder for each release in the same location as the program, and text files within the release's folder (including an `--- info.txt` file with basic identifying info about the release). Each text file is named with the scheme `[Artist Name] - [Track Title].txt` and contains the top five results from each platform searched.

If it seems a search is taking a long time, wait a few minutes. If it still doesn't complete, press Ctrl+C to go back to the menu.
