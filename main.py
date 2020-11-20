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
            if href not in music_urls and ".jpg" not in href:
                music_urls.append(href)
    except KeyError:
        pass

def getDownloadURL(link):
    link_page = requests.get(BASE_URL + link).text
    link_soup = BeautifulSoup(link_page, "html.parser")
    betterFlag = False

    for a in link_soup.find_all("a"):
        try:
            href = a["href"]
            if "vgmsite.com" in href:
                if  ".flac" in href or ".m4a" in href:
                    betterFlag = True
                    if href not in download_urls and "jpg" not in href:
                        download_urls.append(href)
                        #print(href)
                elif ".mp3" in href and betterFlag is True:
                    if href not in download_urls and "jpg" not in href:
                        download_urls.append(href)
                        #print(href)
        except KeyError:
            pass

for link in music_urls: # creates a thread for each download link and puts them in an array
    thread = threading.Thread(target=getDownloadURL, args=(link,))
    threads.append(thread)

for thread in threads: # starts all threads
    thread.start()

for thread in threads: # waits for all threads to finish
    thread.join()

print("Found", len(download_urls), "tracks.")

if os.path.isdir("download"):
    with requests.Session() as req:
        save_path = "download/"
        for file in download_urls:
            print("Downloading file")
            fileName = file.split("/")[-1]
            fileRequest = req.get(file, stream=True)
            with open(os.path.join(save_path, fileName), "wb") as musicFile:
                musicFile.write(fileRequest.content)
                print("Finished downloading file: " + musicFile.name)

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
    print("Please create a folder named 'download' in order to download.")