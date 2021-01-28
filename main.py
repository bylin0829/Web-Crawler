import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import unicodedata

class HtmlParser:
    def __init__(self, url):
        response = requests.get(url)
        self.soup = BeautifulSoup(response.text, "html.parser")
        if url[-1] == '/':
            self.url = url
        else:
            self.url = url+'/'

    def get_title(self):
        x = self.soup.find("h1").get_text()
        return str(x)

    def get_author(self):
        x = self.soup.find("h2").find("span").get_text()
        return str(x)

    def get_content(self, suburl):
        x = self.soup.find("div", class_="content")
        return str(x)
    
    def get_all_chapter(self):
        result = []
        for x in self.soup.find_all("li", class_="chapter", ):
            temp = []
            temp.append(self.url+x.find("a").get("href"))
            temp.append(x.find("a").get_text())
            result.append(temp)
        return result

class Epub:
    def __init__(self, title, author, identifier):
        self.title = title
        self.author = author
        self.identifier = identifier
        self.book = epub.EpubBook()

        self.book.set_identifier(self.identifier)
        self.book.set_title(self.title)
        self.book.set_language('en')
        self.book.add_author(self.author)
    
    def add_chapter(self, content):
        # create chapter
        self.content = content
        self.c1 = epub.EpubHtml(title='介紹一下', file_name='chap_01.xhtml')        
        self.c1.content=self.content
        
        self.c2 = epub.EpubHtml(title='title2', file_name='chap_02.xhtml')        
        self.c2.content='<h1>About this book</h1><p>This is a book.</p>'

        self.book.add_item(self.c1)
        self.book.add_item(self.c2)

        # define Table Of Contents
        self.book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
                            (epub.Section('Simple book'),
                            (self.c1, self.c2))
                        )

    def export_epub(self, book_name=None):
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
        self.book.spine = ['nav', self.c1, self.c2]

        # write to the file
        epub.write_epub(book_name+'.epub', self.book)

if __name__=='__main__':
    url = 'https://tw.aixdzs.com/read/271/271523/'
    x = HtmlParser(url)
    # y = Epub(title=x.get_title(), author=x.get_author(), identifier='id123456')
    # content=x.get_content()
    # y.add_chapter(content)
    # y.export_epub('test0127')
    print(x.get_all_chapter())
    # print(x.get_author())