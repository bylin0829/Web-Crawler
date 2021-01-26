import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import unicodedata

class HtmlParser:
    def __init__(self, url):
        response = requests.get(url)
        self.soup = BeautifulSoup(response.text, "html.parser")
    
    def get_title(self):
        x = self.soup.find("h1").get_text()
        return str(x)

    def get_author(self):
        x = self.soup.find("h2").find("span").get_text()
        return str(x)

    def get_content(self):
        x = self.soup.find("div", class_="content")
        return str(x)

class Epub:
    def __init__(self, title, author, content, identifier):
        self.title = title
        self.author = author
        self.content = content
        self.identifier = identifier
        self.book = epub.EpubBook()

    def export_epub(self):
        # set metadata
        self.book.set_identifier(self.identifier)
        self.book.set_title(self.title)
        self.book.set_language('en')

        self.book.add_author(self.author)
        self.book.add_author('Danko Bananko', file_as='Gospodin Danko Bananko', role='ill', uid='coauthor')

        # create chapter
        c1 = epub.EpubHtml(title='介紹一下', file_name='chap_01.xhtml', lang='hr')
        # c1.content=u'<h1>Hi Chloe!</h1><p>要不要一起去看五月天?</p>'
        c1.content=self.content

        # add chapter
        self.book.add_item(c1)
        c2 = epub.EpubHtml(title='介紹一下2', file_name='chap_02.xhtml', lang='hr')
        c2.content = 'Hello world!'
        self.book.add_item(c2)
        # define Table Of Contents
        # self.book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
        #             (epub.Section('Simple book'),
        #             (c1, ))
        #             )

        # add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)

        # basic spine
        self.book.spine = ['nav', c1]

        # write to the file
        epub.write_epub('test_encoder.epub', self.book, {})

if __name__=='__main__':
    url = 'https://tw.aixdzs.com/read/271/271523/p42.html'
    x = HtmlParser(url)
    y = Epub(title=x.get_title(), author=x.get_author(), content=x.get_content(), identifier='id123456')
    # print(x.get_author())
    # print(x.get_title())
    # print(x.get_content())
    y.export_epub()
    # exportEpub(str(txt))