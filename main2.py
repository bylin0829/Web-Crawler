from hashlib import new
from sys import excepthook
from unittest.result import failfast
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import unicodedata
import os.path
import time
from ebooklib import epub

class my_epub:
    def __init__(self) -> None:
        self.book = epub.EpubBook()

        # set metadata
        self.book.set_identifier('dannylin')
        self.book.set_language('en')
        self._title = None
        self._author = None
        self._directory = []

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, content=''):
        self._title = content
        self.book.set_title(self._title)

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, content=''):
        self._author = content
        self.book.add_author(self._author)
        # book.add_author('Danko Bananko', file_as='Gospodin Danko Bananko', role='ill', uid='coauthor')

    def outline(self, content=''):
        # self._directory.append(y.add_chapter('書籍資訊', '<h2>書籍資訊</h2>'+str(x.get_book_info()), 'book_info.xhtml'))
        # self._directory.append(y.add_chapter('大綱', '<h2>大綱</h2>'+content, 'introduction.xhtml'))
        self.build_page('大綱', 'outline', '<h2>大綱</h2>' + content)

    def build_page(self, title='', file_name='', content=''):
        # create chapter
        c1 = epub.EpubHtml(title=title, file_name='{file_name}.xhtml'.format(file_name=file_name), lang='hr')
        c1.content=u'<h1>{title}</h1><p>{content}</p>'.format(title=title, content=content)
        # add chapter
        self.book.add_item(c1)
        self._directory.append(c1)
        return c1

    def create_directory(self):
        # define Table Of Contents
        self.book.toc=(epub.Link('intro.xhtml', '目錄', 'intro'),
                        (epub.Section('本文'),
                    (tuple(self._directory) ))
                    )
    
    def export(self):
        # add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)

        # basic spine
        # self.book.spine = ['nav', c1]
        self.book.spine = ['nav'] + self._directory
        
        # write to the file
        output_folder = os.path.join(os.path.dirname(__file__), "output")
        output_file = os.path.join(output_folder, self._title+'.epub')
        try:
            os.mkdir(output_folder)            
        except:
            pass
        epub.write_epub(output_file, self.book, {})
        print('輸出路徑: ' + output_file)
        print('Done')

if __name__=='__main__':
    mybook = my_epub()
    mybook.title = input('書名:')
    mybook.author = input('作者:')
    mybook.outline(input('大綱:'))

    failure = []
    url_root = 'https://m.shg.tw'
    url_next = '/246482/2593840.html'
    stop_condition = '/246482/'
    index = 1
    while True:
        try:
            url_chapter = url_root + url_next
            print('Export: {url}'.format(url=url_chapter))
            response=requests.get(url_chapter)
            soup=BeautifulSoup(response.text, "html.parser")
            chapter_title = soup.find_all("h1", class_="headline")[0].text
            contents = soup.find_all('div', class_='content')[0].text
            # new_content = ''
            # for i in contents:
            #     new_content += str(i)
            mybook.build_page(chapter_title, str(index) , contents)
            url_next = soup.find_all('a')[22].attrs['href']
            if url_next == stop_condition:
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            break
        except Exception as e:
            failure.append(index)
            print('Exception')
        finally:
            index += 1
    print('Failure index:{failure}'.format(failure=failure))
    mybook.create_directory()
    mybook.export()
    