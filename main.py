import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import unicodedata
import os.path

class HtmlParser:
    def __init__(self, url_src):
        self.url_src=url_src
        response=requests.get(self.url_src)
        self.soup=BeautifulSoup(response.text, "html.parser")
        if self.url_src[-1] != '/':
            self.url_src=self.url_src+'/'
        self.url_chapter=self.url_src.replace('/d/', '/read/')

    def get_title(self):
        title=self.soup.title.get_text()
        x=title.find('txt')
        if x == -1:
            x=0
        return str(title[:x])

    def get_author(self):
        x=self.soup.find_all('span')
        for index, i in enumerate(x):
            if str(i.get_text()).find('作者')>-1 and str(x[index+1].get_text()).find('分類')>-1:
                return i.next_element.next_element.get_text()
        return '無作者資料'

    def get_intro(self):
        response=requests.get(self.url_src)
        subweb=BeautifulSoup(response.text, "html.parser")
        x=subweb.find("div", class_="d_co")
        return str(x)
    
    def get_book_info(self):
        response=requests.get(self.url_src)
        subweb=BeautifulSoup(response.text, "html.parser")
        x=subweb.find("div", class_="d_ac fdl").find('ul')
        result=''
        for index, i in enumerate(x):
            if index%2 == 1 and index<=9:
                result += str(i)+'\n'
        return result

    def export_chapter_info(self, count=-1):
        self.chapter_info_list=[]
        response=requests.get(self.url_chapter)
        soup=BeautifulSoup(response.text, "html.parser")
        user_confirm=input("總共{count}篇文章, 確定要輸出嗎?(輸入yes或no): ".format(count=len(soup.find_all("li", class_="chapter", ))))
        if(str(user_confirm).lower() == 'y' or str(user_confirm).lower() == 'yes'):
            for x in soup.find_all("li", class_="chapter", ):
                if count > 0:
                    count -= 1
                elif count == 0:
                    break
                else:
                    pass
                temp=[]
                print('Export:' + x.find("a").get_text())
                temp.append(x.find("a").get_text()) # get all of chapter name
                response=requests.get(self.url_chapter+x.find("a").get("href"))
                subweb=BeautifulSoup(response.text, "html.parser")
                temp.append(subweb.find("div", class_="content")) # get all of content
                temp.append(self.url_chapter+x.find("a").get("href")) # get all of links
                self.chapter_info_list.append(temp) # collect all of information into list
        return self.chapter_info_list #[title, content, url]

class Epub:
    def __init__(self, title, author, identifier):
        self.title=title
        self.author=author
        self.identifier=identifier
        self.book=epub.EpubBook()

        print('書籍名稱:' + self.title)
        print('作者:' + self.author)

        self.book.set_identifier(self.identifier)
        self.book.set_title(self.title)
        self.book.set_language('en')
        self.book.add_author(self.author)
    
    def add_chapter(self, chapter_title='Untitled', contents='Content is empty', epub_url=''):
        # create chapter
        x=len(epub_url)
        if x <= 6:
            epub_url += '.xhtml'
        else:
            if epub_url[-6:] != '.xhtml':
                epub_url += '.xhtml'
        c1=epub.EpubHtml(title=chapter_title, file_name=epub_url, lang='hr')
        c1.content=contents
        return c1

    def create_toc(self, chapterinfo):
        self.chapterinfo=chapterinfo
        for i in self.chapterinfo:
            self.book.add_item(i)
        # define Table Of Contents
        self.book.toc=(epub.Link('intro.xhtml', '目錄', 'intro'),
                            (epub.Section('本文'),
                            tuple(self.chapterinfo))
                        )

    def export_epub(self, book_name):
        # set metadata

        # add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # define CSS style
        style='BODY {color: white;}'
        nav_css=epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book.add_item(nav_css)

        # basic spine
        self.book.spine=['nav'] + self.chapterinfo

        # write to the file
        output_folder = os.path.join(os.path.dirname(__file__), "output")
        output_file = os.path.join(output_folder, book_name+'.epub')
        try:
            mkdir(output_folder)            
        except:
            pass
        epub.write_epub(output_file, self.book, {})
        print('輸出路徑: ' + output_file)
        print('Done')

if __name__=='__main__':
    # url_src='https://tw.aixdzs.com/d/271/271523/'
    url_src=input('請輸入愛下電子書網址\n範例: https://tw.aixdzs.com/d/264/264211/ \n您的輸入: ')
    x=HtmlParser(url_src)
    x.get_book_info()
    
    # Create epub class
    y=Epub(title=x.get_title(), author=x.get_author(), identifier='id123456')

    # Add introduction page
    chapter_list=[]
    chapter_list.append(y.add_chapter('書籍資訊', '<h2>書籍資訊</h2>'+str(x.get_book_info()), 'book_info.xhtml'))
    chapter_list.append(y.add_chapter('大綱', '<h2>大綱</h2>'+str(x.get_intro()), 'introduction.xhtml'))

    # Add chapter
    for index, i in enumerate(x.export_chapter_info()):
        test_content=str(i[1])
        header='<h1>{0}</h1>'.format(i[0])
        chapter_list.append(y.add_chapter(chapter_title= i[0], contents=header + test_content, epub_url='page'+str(index))) #[title, content, url]
    
    if len(chapter_list) <= 2:
        print("無文章或使用者終止")
    else:
        # Create table of content
        y.create_toc(chapter_list)

        # Export epub
        y.export_epub(x.get_title())