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
        title = self.soup.title.get_text()
        x = title.find('txt')
        if x == -1:
            x = 0
        return str(title[:x])

    def get_author(self):
        x = self.soup.find_all('span')
        for index, i in enumerate(x):
            if str(i.get_text()).find('作者')>-1 and str(x[index+1].get_text()).find('分類')>-1:
                return i.next_element.next_element.get_text()
        return '無作者資料'

    def get_intro(self):
        response = requests.get(self.url_src)
        subweb = BeautifulSoup(response.text, "html.parser")
        x = subweb.find("div", class_="d_co")
        return str(x)
    
    def get_book_info(self):
        response = requests.get(self.url_src)
        subweb = BeautifulSoup(response.text, "html.parser")
        # x = subweb.find("ul").find_all('li')
        x = subweb.find("div", class_="d_ac fdl").find('ul')
        result = ''
        for index, i in enumerate(x):
            if index%2 == 1 and index<=9:
                result += str(i)+'\n'
                # print(index)
                # print(i)
        # print(result)
        return result

    def get_chapter_info(self, count=-1):
        self.chapter_info_list = []
        response = requests.get(self.url_chapter)
        soup = BeautifulSoup(response.text, "html.parser")
        for x in soup.find_all("li", class_="chapter", ):
            if count > 0:
                count -= 1
            elif count == 0:
                break
            else:
                pass
            temp = []
            print('Export:' + x.find("a").get_text())
            temp.append(x.find("a").get_text()) # get all of chapter name
            response = requests.get(self.url_chapter+x.find("a").get("href"))
            subweb = BeautifulSoup(response.text, "html.parser")
            temp.append(subweb.find("div", class_="content")) # get all of content
            temp.append(self.url_chapter+x.find("a").get("href")) # get all of links
            self.chapter_info_list.append(temp) # collect all of information into list
        return self.chapter_info_list #[title, content, url]

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
    
    def add_chapter(self, chapter_title='Untitled', contents='Content is empty', epub_url=''):
        # create chapter
        x = len(epub_url)
        if x <= 6:
            epub_url += '.xhtml'
        else:
            if epub_url[-6:] != '.xhtml':
                epub_url += '.xhtml'
        c1 = epub.EpubHtml(title=chapter_title, file_name=epub_url, lang='hr')
        c1.content = contents
        return c1

    def create_toc(self, chapterinfo):
        self.chapterinfo = chapterinfo
        for i in self.chapterinfo:
            self.book.add_item(i)
        # define Table Of Contents
        self.book.toc = (epub.Link('intro.xhtml', '目錄', 'intro'),
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
        print(book_name+'.epub')
        epub.write_epub(book_name+'.epub', self.book, {})
        print('==epub export successfully==')

if __name__=='__main__':
    # url_src = 'https://tw.aixdzs.com/d/271/271523/'
    url_src = input('source url:')
    x = HtmlParser(url_src)
    # print(x.get_intro())
    # print(x.get_author())
    # print(x.get_title())
    x.get_book_info()
    # Create epub class

    y = Epub(title=x.get_title(), author=x.get_author(), identifier='id123456')

    # Add introduction page
    chapter_list = []
    chapter_list.append(y.add_chapter('書籍資訊', '<h2>書籍資訊</h2>'+str(x.get_book_info()), 'book_info.xhtml'))
    chapter_list.append(y.add_chapter('大綱', '<h2>大綱</h2>'+str(x.get_intro()), 'introduction.xhtml'))
    # Add chapter
    for index, i in enumerate(x.get_chapter_info()):
        # test_content = str(i[1]).replace('<div class="content">','').replace('</div>','')
        test_content = str(i[1])
        header = '<h1>{0}</h1>'.format(i[0])
        chapter_list.append(y.add_chapter(chapter_title= i[0], contents=header + test_content, epub_url='page'+str(index))) #[title, content, url]
    
    # Create table of content
    y.create_toc(chapter_list)

    # Export epub
    y.export_epub(x.get_title())