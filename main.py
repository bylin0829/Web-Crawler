import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import unicodedata

class HtmlParser:
    def __init__(self, url_src):
        self.url_src = url_src
        response = requests.get(self.url_src)
        self.soup = BeautifulSoup(response.text, "html.parser")
        if self.url_src[-1] != '/':
            self.url_src = self.url_src+'/'
        self.url_chapter = self.url_src.replace('/d/', '/read/')

    def get_title(self):
        x = self.soup.find("h1").get_text()
        return str(x)

    def get_author(self):
        x = self.soup.find("h2").find("span").get_text()
        return str(x)
    
    def get_test(self):
        x = self.soup.find_all('span')
        for index, i in enumerate(x):
            print(index)
            if str(i.get_text()).find('作者')>-1 and str(x[index+1].get_text()).find('分類')>-1:
                print('got it in index='+str(index))
                break

        # for i in self.soup.find_all():

    def get_intro(self):
        response = requests.get(self.url_src)
        subweb = BeautifulSoup(response.text, "html.parser")
        x = subweb.find("div", class_="d_co")
        return str(x)

    def get_chapter_info(self, count=10):
        self.chapter_info_list = []
        for x in self.soup.find_all("li", class_="chapter", ):
            if count > 0:
                count -= 1
                temp = []
                temp.append(self.url_chapter+x.find("a").get("href"))
                temp.append(x.find("a").get_text())
                response = requests.get(self.url_chapter+x.find("a").get("href"))
                subweb = BeautifulSoup(response.text, "html.parser")
                temp.append(subweb.find("div", class_="content"))
                self.chapter_info_list.append(temp)
        return self.chapter_info_list

class Epub:
    def __init__(self, title, author, identifier):
        self.title = title
        self.author = author
        self.identifier = identifier
        self.book = epub.EpubBook()

        print('title:' + self.title)
        print('author:' + self.author)

        self.book.set_identifier(self.identifier)
        self.book.set_title(self.title)
        self.book.set_language('en')
        self.book.add_author(self.author)
    
    # def add_intro(self):
    #     self.url

    def add_chapter(self, chapter_title='Untitled', content='Content is empty', epub_url=''):
        # create chapter
        # c1 = epub.EpubHtml(title='介紹一下', file_name='chap_01.xhtml')    
        x = len(epub_url)
        if x <= 6:
            epub_url += '.xhtml'
        else:
            if epub_url[-6:] != '.xhtml':
                epub_url += '.xhtml'
        c1 = epub.EpubHtml(title=chapter_title, file_name=epub_url)
        c1.content = content
        print('file_name:' + epub_url)
        return c1

    def create_toc(self, subtitle, chapterinfo):
        self.subtitle = subtitle
        self.chapterinfo = chapterinfo
        for i in chapterinfo:
            self.book.add_item(i)
        # self.book.add_item(self.c2)
        # define Table Of Contents
        self.book.toc = (epub.Link('introduction.xhtml', '介紹', 'intro'),
                            (epub.Section('本文'),
                            tuple(self.chapterinfo))
                        )

    def export_epub(self, book_name):
        # set metadata

        # add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)

        # basic spine
        self.book.spine = ['nav'] + self.chapterinfo

        # write to the file
        epub.write_epub(book_name+'.epub', self.book)

if __name__=='__main__':
    url_src = 'https://tw.aixdzs.com/d/271/271523/'
    x = HtmlParser(url_src)
    # print(x.get_intro())
    x.get_test()
    # print(x.get_title())
    # print(x.get_author())
    # print(x.get_chapter_info())


    # y = Epub(title=x.get_title(), author=x.get_author(), identifier='id123456')    
    # counter = 1
    # chapter_list = []
    # for i in x.get_chapter_info(5):
    #     chapter_list.append(y.add_chapter(i[1], 'page'+str(counter)))
    #     counter += 1
    # y.create_toc('myname',chapter_list)
    # y.export_epub('test_book_0130')