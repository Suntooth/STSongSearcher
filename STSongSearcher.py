# you need to replace these with your own tokens. it's up here so it's easy to find
SPOTIFY_CLIENT_ID = "PUT YOUR SPOTIFY CLIENT ID HERE"
SPOTIFY_SECRET_KEY = "PUT YOUR SPOTIFY SECRET KEY HERE"
DISCOGS_TOKEN = "PUT YOUR DISCORD USER TOKEN HERE"









# i know it's really bad practice to put any code before imports, but otherwise it's delayed showing up
# which defeats the entire purpose of this print
print("Initialising...")


# imports
import os
import sys
import json
import traceback
import discogs_client
from time import sleep
from random import randint
from py_bandcamp import BandCamp
from spotify_client import SpotifyClient
from youtube_search import YoutubeSearch


# functions

def getURL(inp, types):
    if types == "master":
        url = "https://www.discogs.com/master/" + str(inp.id)
    else:
        url = "https://www.discogs.com/release/" + str(inp.id)
    return url


def getFullName(inp, types):
    if types == "master":
        artist = inp.main_release.artists[0].name
    else:
        artist = inp.artists[0].name

    fullName = artist + " - " + inp.title
    return fullName


# remove the e.g. (2) disambiguator from the end of discogs names (i still don't understand why this isn't done with anvs)
# it will hit false positives on artist names that end with a closing bracket, but the search results should work anyway
# and if in doubt i should be searching manually anyway
def removeDab(inp):
    # out = inp means that if there's no dab it just returns the input
    out = inp
    # if the input ends with a closing bracket
    if inp[-1] == ")":
        # rsplit is split but from the right side instead of the left side, and the 1 limits it to 1 split - so just the last instance
        splitted = inp.rsplit(" (", 1)
        out = splitted[0]
    return out


# do a search then pick a random release from that search
# example: format="Sampler", type="master", genre="Rock", artist="Various"
def findRandomFromSearch():
    # initialise these variables early to avoid an error
    randomResult = ""
    releaseFullName = ""
    
    typeC = "master" if input("[M]aster or [R]elease? ").lower() == "m" else "release"
    print("\n[All following options accept a blank response.]\n")
    sleep(0.5)
    queryC = input("General query: ")
    titleC = input("Title: ")
    artistC = input("Artist: ")
    anvC = input("ANV: ")
    formatC = input("Format (such as CD or album or compilation): ")
    trackC = input("Track title: ")
    genreC = input("Genre: ")
    styleC = input("Style: ")
    labelC = input("Label: ")
    countryC = input("Release country: ")
    yearC = input("Year: ")
    creditC = input("Credited artist: ")
    catnoC = input("Catalog number: ")
    barcodeC = input("Barcode: ")
    print("\nWait a moment...\n")
    
    # searching discogs
    results = d.search(query=queryC, type=typeC, release_title=titleC, credit=creditC, artist=artistC,
                       anv=anvC, label=labelC, genre=genreC, style=styleC, country=countryC,
                       year=yearC, format=formatC, catno=catnoC, barcode=barcodeC, track=trackC)
    
    # choose a random result from the search
    # discogs caps search results at 10000 but len(results) will go over that
    # so pick a number between 0 and 9999 or the number of results, whichever is lower
    # if there's no results it throws ValueError (because len(results) isn't a valid value in that case)
    try:
        randomInteger = randint(0,min(len(results)-1,9999))
    except ValueError:
        print("No results.\n")
    else:
        try:
            # sometimes this just doesn't work for no reason! oh well
            randomResult = results[randomInteger]
        except:
            print("Error - try again. (This is usually a bug with the Discogs API.)\n")
        else:
            releaseFullName = getFullName(randomResult, typeC)
            resultURL = getURL(randomResult, typeC)
                
            print("\nRandom result:", randomResult)
            print("URL of result:", resultURL)
            
        print("")
    return randomResult, releaseFullName, resultURL


# find a specific release (master or otherwise) by its id
def findSpecificRelease():
    typeC = "master" if input("[M]aster or [R]elease? ").lower() == "m" else "release"
    releaseChoice = input("Enter the release's numerical ID: ")
    print("")
    
    if typeC == "master":
        specificResult = d.master(releaseChoice)
    else:
        specificResult = d.release(releaseChoice)
        
    releaseFullName = getFullName(specificResult, typeC)
    resultURL = getURL(specificResult, typeC)
        
    print("\nResult:", specificResult)
    print("URL of result:", resultURL)
    print("")
        
    return specificResult, releaseFullName, resultURL


# get the tracklist, go through every track, create a string in the format "artist - track", then add that to a list
def getTracks(inp):
    tracksList = []
    
    for track in inp.tracklist:
        try:
            # first case: has an artist assigned specifically to the track (e.g. compilations)
            # if this fails it throws IndexError (there is an artists field, but no artists listed in it)
            toAppend = removeDab(track.artists[0].name) + " - " + track.title
        except IndexError:
            try:
                # second case: normal release (e.g. a specific release of a normal album by an artist)
                # if this fails it throws AttributeError (there's no artists field on the track at all)
                toAppend = removeDab(inp.artists[0].name) + " - " + track.title
            except AttributeError:
                # third case: master release
                toAppend = removeDab(inp.main_release.artists[0].name) + " - " + track.title
            
        tracksList.append(toAppend)
        
    return tracksList


# search spotify for the track
def spotifySearch(inp):
    # search for tracks that match "artist - track", limited to five results since we don't need more than that
    spResults = sp.search(inp, "track", 5)
    # it's known that there will be five results no matter what
    # so we can just loop five times without worrying about the length of what's returned
    for i in range(5):
        # figuring this out sucked. it's just traversing through the dict by looking up keys
        # but also [i] for each individual track because that's a list. and [0] for artists because that's a list
        toWrite = (str(spResults["tracks"]["items"][i]["external_urls"]["spotify"]) + " --- " +
              str(spResults["tracks"]["items"][i]["artists"][0]["name"]) + " - " +
              str(spResults["tracks"]["items"][i]["name"]) + " --- " +
              str(spResults["tracks"]["items"][i]["album"]["name"]))
        
        txt.write(toWrite + "\n")
        
        
# search bandcamp for the track
def bandcampSearch(inp):
    # bc.search_tracks does exist but kept timing out
    bcResults = bc.search(inp)
        
    # there's no parameter to limit bandcamp results and sometimes generic names return a lot of things, so we just iterate it instead
    count = 0
    for item in bcResults:
        try:
            itemData = item.get_album_data(item)
        except:
            try:
                itemData = item.get_track_data(item)
            except:
                itemType = "Artist"
            else:
                itemType = "Track"
        else:
            itemType = "Album"
        
        if itemType == "Artist":
            toWrite = ""
            
        else:
            toWrite = (itemData["url"] + " --- " +
                       itemData["title"] + " --- " +
                       itemType)
        
        txt.write(toWrite + "\n")
        count += 1
        if count == 5:
            break
    
    
# search youtube for the track (not to be confused with YoutubeSearch, which is from the youtube_search module)
def youtubeSearch(inp):
    #needs to be either to_dict or to_json, but to_dict seems bugged so get the json and turn it into a dict with json.loads
    ytResults = json.loads(YoutubeSearch(inp, max_results=5).to_json())
    
    # could probably do range(5) for this too but this works while it didn't for spotify, so may as well futureproof
    for j in range(len(ytResults["videos"])):
        toWrite = (str(ytResults["videos"][j]["id"]) + " --- " +
              str(ytResults["videos"][j]["title"]) + " --- " +
              str(ytResults["videos"][j]["channel"]))
        
        txt.write(toWrite + "\n")


# initialising the clients
# youtube doesn't need initialising bc it's not using the api
# technically bandcamp also isn't using the api (because there isn't an api) but it still needs initialising
d = discogs_client.Client("STSongSearcher/1.0.0-public", user_token=DISCOGS_TOKEN)
sp = SpotifyClient(SPOTIFY_CLIENT_ID, SPOTIFY_SECRET_KEY, identifier='STSongSearcher/1.0.0-public')
bc = BandCamp()


# main program

while True:
    searchChoice = input("""
[0] Quit
[1] Random from a seach
[2] Specific release
Choose an option: """)
    print("")

    if searchChoice == "1":
        release, releaseName, releaseURL = findRandomFromSearch()
    elif searchChoice == "2":
        try:
            release, releaseName, releaseURL = findSpecificRelease()
        except discogs_client.exceptions.HTTPError:
            print("Invalid response. This is usually because the release associated with this ID does not exist or was deleted.")
            sleep(1)
    else:
        sys.exit()
        
    try:
        tracks = getTracks(release)
        
    except:
        # whenever this shows up it just prints the stack trace
        # which means an error won't stop the whole program unless i want it to
        # but i can still see what went wrong when looking at the log
        #print(traceback.format_exc())
        continue
        
    # only run this code if there was not an exception in the previous try-except (because if the previous step fails, all of this will fail too)
    else:
        dirName = str(release.id) + " --- " + str(releaseName).replace("/", "-")
        infoName = dirName + "/--- info.txt"
        try:
            os.mkdir(dirName)
        except FileExistsError:
            print("Warning: Folder for this release already exists. Files will be overwritten.")
        
        with open(infoName, "w") as info:
            info.write(releaseName + "\n")
            info.write(releaseURL + "\n\n")
            info.write("Tracklist:\n")
        
        # go through the list of tracks one by one
        for trackSearch in tracks:
            with open(infoName, "a") as info:
                info.write(trackSearch + "\n")
            
            txtName = dirName + "/" + trackSearch.replace("/", "-") + ".txt"
            with open(txtName, "w") as txt:
                print("")
                print(trackSearch)
                txt.write(trackSearch)
                
                txt.write("\n\n\n=== Spotify ===\n\n")
                print("Searching Spotify...")
                
                try:
                    spotifySearch(trackSearch)
                        
                except KeyboardInterrupt:
                    print("")
                    break
                    
                except:
                    print(traceback.format_exc())
                      
                txt.write("\n\n\n=== Bandcamp ===\n\n")
                print("Searching Bandcamp...")
                # this NEEDS to be in a try/except because py_bandcamp is really buggy and throws a lot of errors i can't do anything about
                try:
                    bandcampSearch(trackSearch)
                    
                except KeyboardInterrupt:
                    print("")
                    break
                    
                except:
                    print(traceback.format_exc())
                
                
                txt.write("\n\n\n=== Youtube ===\n\n")
                print("Searching YouTube...")
                
                try:
                    youtubeSearch(trackSearch)
                        
                except KeyboardInterrupt:
                    print("")
                    break
                    
                except:
                    print(traceback.format_exc())
                    
                print("\n")
        print("Done.\n\n")
