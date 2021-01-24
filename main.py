import requests
from bs4 import BeautifulSoup
from ebooklib import epub

def test2(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find_all("div", class_="content")

def exportEpub(txt):
    book = epub.EpubBook()
    # set metadata
    book.set_identifier('id123456')
    book.set_title('Sample book 測試中文哦!')
    book.set_language('en')

    book.add_author('DannyLin 丹丹漢堡')
    book.add_author('Danko Bananko', file_as='Gospodin Danko Bananko', role='ill', uid='coauthor')

    # create chapter
    c1 = epub.EpubHtml(title='介紹一下', file_name='chap_01.xhtml', lang='hr')
    # c1.content=u'<h1>Hi Chloe!</h1><p>要不要一起去看五月天?</p>'
    c1.content=txt

    # add chapter
    book.add_item(c1)

    # define Table Of Contents
    book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
                (epub.Section('Simple book'),
                (c1, ))
                )

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = ['nav', c1]

    # write to the file
    epub.write_epub('test1.epub', book, {})

if __name__=='__main__':
    txt = test2('https://tw.aixdzs.com/read/166/166552/p1.html')
    exportEpub(txt)