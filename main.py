import requests
import threading
from tinytag import TinyTag
import os
from bs4 import BeautifulSoup
from termcolor import colored

BASE_URL = "https://downloads.khinsider.com"
SEARCH_PARTIAL = "/search?search="

def getSearchResults(search):
    page = requests.get(BASE_URL + SEARCH_PARTIAL + search).text
    soup = BeautifulSoup(page, "html.parser")

    data_div = soup.find(id="EchoTopic")
    results_div = data_div.findAll(align="left")[1]
    return results_div.findAll("a")
    
def getMusicURLs(link):
    page = requests.get(link).text
    soup = BeautifulSoup(page, "html.parser")
    urls = []

    for a in soup.findAll("a"):
        try:
            href = a["href"]
            if link.split("/")[-1] in href:
                if href not in urls and ".jpg" not in href:
                    urls.append(href)
        except KeyError:
            pass

    return urls

def getDownloadURL(link):
    page = requests.get(BASE_URL + link).text
    soup = BeautifulSoup(page, "html.parser")
    betterFlag = False

    for a in soup.find_all("a"):
        try:
            href = a["href"]
            if "vgmsite.com" or "vgmdownloads.com" in href:
                if  ".flac" in href or ".m4a" in href:
                    betterFlag = True
                    if href not in download_urls and "jpg" not in href:
                        download_urls.append(href)
                elif ".mp3" in href and betterFlag is False:
                    if href not in download_urls and "jpg" not in href:
                        download_urls.append(href)
        except KeyError:
            pass

search = input("Enter your search term: ")

if " " in search:
    search = search.replace(" ", "+")

results = getSearchResults(search)

i = 0
for a in results:
    cIndex = colored(str(i), "red")
    cResult = colored(a["href"].split("/")[-1].replace("-", " ").title(), "cyan")
    print(cIndex, "-", cResult)
    i += 1

album_index = input("Select an album from the list: ")
album_link = results[int(album_index)]["href"]

music_urls = getMusicURLs(album_link)
download_urls = []
threads = []

for link in music_urls:
    thread = threading.Thread(target=getDownloadURL, args=(link,))
    threads.append(thread)
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(colored(("Found " + str(len(download_urls)) + " tracks."), "green"))

if os.path.isdir("download"):
    with requests.Session() as req:
        save_path = "download/"
        for file in download_urls:
            print(colored("Downloading file", "yellow"))
            fileName = file.split("/")[-1]
            fileRequest = req.get(file, stream=True)
            with open(os.path.join(save_path, fileName), "wb") as musicFile:
                musicFile.write(fileRequest.content)
                print(colored(("Finished downloading file: " + musicFile.name), "green"))

    for file in os.listdir("download"):
        tag = TinyTag.get(os.path.join("download", file))
        newName = tag.title
        filePath = os.path.join("download", file)
        if "/" in newName:
            newName = newName.replace("/", "-")
        newNamePath = os.path.join("download", newName)
        if file.endswith(".m4a"):
            os.rename(filePath, newNamePath + ".m4a")
        elif file.endswith(".flac"):
            os.rename(filePath, newNamePath + ".flac")
        elif file.endswith(".mp3"):
            os.rename(filePath, newNamePath + ".mp3")
else:
    print("Please create a folder named 'download' in the root in order to download.")