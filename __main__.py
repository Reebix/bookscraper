import logging
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import npyscreen
from ebooklib import epub

from common.common import check_internet_connection, clear_screen

baseurl = "https://www.kostenlosonlinelesen.net"

class Scraper:
    def __init__(self, url, output, progress):
        self.url = url
        self.output = output
        self.progress = progress

    def scrape(self):
        print(f"Scraping {self.url} to {self.output}")
        text = ""
        last = 0

        req = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')
        title = soup.find('h1').text
        text += str(soup.find(class_='txt-cnt'))

        next = soup.find_all('a')

        for i in next:
            try:
                if int(i.text) > last:
                    last = int(i.text)
            except:
                continue

        for i in next:
            if i.text == '»':
                next = i['href']
                break

        while next:
            req = Request(baseurl + next, headers={'User-Agent': 'Mozilla/5.0'})

            self.progress.value = next.split('/')[-1] + "/" + str(last) + " " + str(int(next.split('/')[-1]) * 100 // last) + "%"
            self.progress.display()

            webpage = urlopen(req).read()

            soup = BeautifulSoup(webpage, 'html.parser')
            text += str(soup.find(class_='txt-cnt'))

            next = soup.find_all('a')
            found = False

            for i in next:
                if i.text == '»':
                    next = i['href']
                    found = True
                    break

            if not found:
                break

        self.create_epub(title, text)
        print(f"\n\nScraped {self.url} to {self.output}/{title}.epub")

    def create_epub(self, title, text):
        book = epub.EpubBook()
        book.set_title(title)
        book.set_language('de')
        book.add_author('Terry Pratchett')

        chapter = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
        chapter.content = f'<h1>{title}</h1>{text}'
        book.add_item(chapter)

        # book.toc = (epub.Link('chap_01.xhtml', 'Chapter 1', 'chap_01'),)
        book.spine = ['nav', chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub(f'{self.output}/{title}.epub', book, {})

class MainForm(npyscreen.ActionForm):
    def create(self):
        self.url = self.add(npyscreen.TitleText, name="URL: ")
        self.list = self.add(npyscreen.TitleFilenameCombo, name="List(Optional): ")
        self.output = self.add(npyscreen.TitleFilenameCombo, name="Output: ")
        self.progress = self.add(npyscreen.TitleFixedText, name="Current: ", value="", relx=2, rely=6, editable=False)

    def on_cancel(self):
        self.parentApp.switchForm(None)

    def on_ok(self):
        self.parentApp.setNextForm(None)
        self.parentApp.switchForm(None)

        if self.list.value:
            with open(self.list.value, 'r') as f:
                urls = f.readlines()
                for url in urls:
                    url = url.strip()
                    if url:
                        scraper = Scraper(url, self.output.value, self.progress)
                        scraper.scrape()
        else:
            scraper = Scraper(self.url.value, self.output.value, self.progress)
            scraper.scrape()

class ScraperApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Scraper")

def main():
    if not check_internet_connection():
        clear_screen()
        logging.disable(logging.CRITICAL)
        sys.exit()
    app = ScraperApp()
    app.run()

if __name__ == '__main__':
    main()