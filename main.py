import requests
import threading
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
            if "flac" in href or "m4a" in href:
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