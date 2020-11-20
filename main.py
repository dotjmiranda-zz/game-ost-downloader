import requests
import threading
from tinytag import TinyTag
import os
from bs4 import BeautifulSoup

BASE_URL = "https://downloads.khinsider.com"
URL = input("Enter the album's link: ")

page = requests.get(URL).text
soup = BeautifulSoup(page, "html.parser")

music_urls = []
download_urls = []
threads = []

for a in soup.find_all("a"): # iterate through all <a> tags
    try:
        href = a["href"]
        if URL.split("/")[-1] in href: # check for duplicate links
            if href not in music_urls:
                music_urls.append(href)
    except KeyError:
        pass

def getDownloadURL(link):
    link_page = requests.get(BASE_URL + link).text
    link_soup = BeautifulSoup(link_page, "html.parser")

    for a in link_soup.find_all("a"):
        try:
            href = a["href"]
            if "vgmsite.com" in href and ".flac" in href or ".m4a" in href:
                if href not in download_urls and "jpg" not in href:
                    download_urls.append(href)
                    print(href)
            elif "vgmsite.com" in href and ".mp3" in href:
                if href not in download_urls and "jpg" not in href:
                    download_urls.append(href)
                    print(href)
        except KeyError:
            pass

for link in music_urls: # creates a thread for each download link and puts them in an array
    thread = threading.Thread(target=getDownloadURL, args=(link,))
    threads.append(thread)

for thread in threads: # starts all threads
    thread.start()

for thread in threads: # waits for all threads to finish
    thread.join()

with requests.Session() as req:
    for file in download_urls:
        print("Downloading File")
        fileName = file.split("/")[-1]
        fileRequest = req.get(file, stream=True)
        with open(fileName, "wb") as musicFile:
            musicFile.write(fileRequest.content)
        print("Finished download File")

for file in os.listdir():
    if file.endswith(".m4a") or file.endswith(".flac") or file.endswith(".mp3"):
        tag = TinyTag.get(file)
        newName = tag.title
        if "/" in newName:
            newName = newName.replace("/", "-")
        if file.endswith(".m4a"):
            tag = TinyTag.get(file)
            os.rename(file, newName + ".m4a")
        elif file.endswith(".flac"):
            tag = TinyTag.get(file)
            os.rename(file, newName + ".flac")
        elif file.endswith(".mp3"):
            tag = TinyTag.get(file)
            os.rename(file, newName + ".mp3")