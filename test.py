from tkinter.ttk import Style
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import unicodedata
import os.path

url_chapter = "https://m.shg.tw/246482/2593842.html"
response=requests.get(url_chapter)
soup=BeautifulSoup(response.text, "html.parser")

# x = soup.find_all("a", class_="pt-nextchapter")[0].attrs['href']
# x = soup.find_all('a')[22].attrs['href']
x = soup.find_all('div', class_='content')[0].text
print('test')