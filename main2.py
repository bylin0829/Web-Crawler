import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import os.path
from hashlib import md5
from time import time
from opencc import OpenCC


class my_epub:
    def __init__(self) -> None:
        self.book = epub.EpubBook()

        # set metadata
        idf = md5()

        idf.update(str(time()).encode())
        self.book.set_identifier(idf.hexdigest())
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

    @property
    def outline(self):
        pass

    @outline.setter
    def outline(self, content=''):
        self.build_page('大綱', 'outline', '<h2>大綱</h2>' + content)

    def build_page(self, title='', file_name='', content=''):
        # create chapter
        c1 = epub.EpubHtml(title=title, file_name='{file_name}.xhtml'.format(
            file_name=file_name), lang='hr')
        c1.content = u'<h1>{title}</h1><p>{content}</p>'.format(
            title=title, content=content)
        # add chapter
        # if file_name != 'outline':
        self.book.add_item(c1)
        self._directory.append(c1)
        return c1

    def create_directory(self):
        # define Table Of Contents
        self.book.toc = (epub.Link('outline.xhtml', '大綱', 'intro'),
                         (epub.Section('�?�?'),
                         (tuple(self._directory[1:])))
                         )

    def export(self):
        # add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(
            uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

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
        print('Output file: ' + output_file)
        print('Done')


def books_build_flow(book_name, book_url, author, outline):
    DEBUG = False
    mybook = my_epub()
    cc = OpenCC('s2tw')
    mybook.title = book_name
    mybook.author = author
    outline = outline.replace('\r\n', '<br>')
    mybook.outline = cc.convert(outline)

    failure = []
    url_root = book_url
    url_root = url_root.replace('index.htm', '')

    url_next = '01.htm'
    stop_condition = 'index.htm'
    next_page_condition = ''  # combine content if the link includes this word
    chapter_index = 1
    full_content = ''

    while True:
        try:
            # Import html information by bs4
            url_chapter = url_root + url_next

            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url_chapter, headers=headers)
            response.encoding = 'gb2312'
            soup = BeautifulSoup(response.text, "html.parser")
            print('Export: {url}'.format(url=url_chapter))

            # Find title and remove useless words
            title_tag = 'td'
            title_class = 'td2'
            title_useless_words = ''
            title = soup.find_all(title_tag, class_=title_class)[0].text
            # method 1
            title = title.replace(title_useless_words, '')
            title = title.replace('��', 'O')

            # method 2
            # title_useless_words_idx = title.find(title_useless_words)
            # if title_useless_words_idx > -1:
            #     title = title[:title_useless_words_idx]
            title = cc.convert(title)
            print(title)

            # Filter content for useless words
            content_tag = 'td'
            content_class = ''
            content_useless_words = '\r\n'
            content_replace_to = '<br>'
            content = soup.find_all(
                name=content_tag, class_=content_class)[0].text

            # method 1
            content = content.replace(
                content_useless_words, content_replace_to)
            # content = content.replace('???', '')
            # method 2
            # content_useless_words_idx = content.find(content_useless_words)
            # if content_useless_words_idx > -1:
            #     content = content[:content_useless_words_idx]
            content = cc.convert(content)

            # Find next page or chapter link
            next_tag = 'a'
            next_class = ''

            # method 1
            # next_button_idx = 2
            # url_next = soup.find_all(name=next_tag, class_ = next_class)[next_button_idx].attrs['href']
            # method 2
            try:
                url_next = soup.find_all(name=next_tag, string="下一页")[
                    0].attrs['href']
                # print('下一頁')
            except Exception as e:
                url_next = soup.find_all(name=next_tag, string="下一章")[
                    0].attrs['href']
                # print('下一章')

            # Check contents finished or not
            full_content += content
            #############
            if url_next.find(next_page_condition) != -1:
                mybook.build_page(title, str(chapter_index), full_content)
                print('Add page')
                if DEBUG == True:
                    print(full_content)
                    print('Debug mode')
                    raise KeyboardInterrupt
                full_content = ''
                chapter_index += 1
            if url_next.find(stop_condition) > -1:
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            break
        except Exception as e:
            failure.append(chapter_index)
            print('Exception')
            if len(failure) > 5:
                break

    print('Failure index:{failure}'.format(failure=failure))
    mybook.create_directory()
    mybook.export()


if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Get outline

    books = [
        ['木蘭花系列53-電網火花', 'https://www.xuges.com/kh/nk/a53/index.htm', '倪匡'],
        ['木蘭花系列54-古屋奇影', 'https://www.xuges.com/kh/nk/a54/index.htm', '倪匡'],
        ['木蘭花系列55-金廟奇佛', 'https://www.xuges.com/kh/nk/a55/index.htm', '倪匡'],
        ['木蘭花系列56-天才白痴', 'https://www.xuges.com/kh/nk/a56/index.htm', '倪匡'],
        ['木蘭花系列57-生命合同', 'https://www.xuges.com/kh/nk/a57/index.htm', '倪匡'],
        ['木蘭花系列58-三尸同行', 'https://www.xuges.com/kh/nk/a58/index.htm', '倪匡'],
        ['木蘭花系列59-無風自動', 'https://www.xuges.com/kh/nk/a59/index.htm', '倪匡'],
        ['木蘭花系列60-無名怪屍', 'https://www.xuges.com/kh/nk/a60/index.htm', '倪匡'],
        ['浪子高達系列1-微晶之秘', 'https://www.xuges.com/kh/nk/wjzm/index.htm', '倪匡'],
        ['浪子高達系列2-超腦終極戰', 'https://www.xuges.com/kh/nk/cnzj/index.htm', '倪匡'],
        ['浪子高達系列3-血美人', 'https://www.xuges.com/kh/nk/xmr/index.htm', '倪匡']


    ]
    for i in books:
        response = requests.get(i[1], headers=headers)
        response.encoding = 'gb2312'
        soup = BeautifulSoup(response.text, "html.parser")
        print('Export: {url}'.format(url=i[1]))
        try:
            outline = soup.find_all('td', class_='zhj')[0].text
        except:
            outline = ''
        # outline = outline.replace()
        # print(outline)
        books_build_flow(book_name=i[0], book_url=i[1],
                         author=i[2], outline=outline)
