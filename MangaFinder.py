# -*- coding: UTF-8 -*-

import urllib2
import argparse
import sys
import logging
from bs4 import BeautifulSoup
import MangaDownloader


def get_arguments():
        parser = argparse.ArgumentParser()
        parser.add_argument('url', metavar='URL', type=str, help="URL of manga chapter from McAnime.net")
        parser.add_argument('title', metavar='title', type=str, help="Title of the manga")
        parser.add_argument('-k', action='store_true', help="Enable conversion to kindle (.mobi output)")
        parser.add_argument('-n', nargs=1, type=int, help="Download the chapter specified")
        parser.add_argument('-f', nargs=2, type=int, help="Download the chapters between the specified numbers "
                                                          "(including them)")
        parser.add_argument('-l', nargs='+', type=str, help="Specify one or more language of searching")
        args = parser.parse_args()

        return args

class MangaFinder():

    MC_DOMAIN = "http://www.mcanime.net"
    LOG_FILE = "log.log"

    def __init__(self, args):

        logging.basicConfig(filename=self.LOG_FILE, level=logging.DEBUG,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("MangaFinder")

        self.url = args.url
        self.title = args.title
        self.convert = args.k

        if args.n is not None:
            self.start = int(args.n[0])
            self.end = int(args.n[0])
        elif args.f is not None:
            self.start = int(args.f[0])
            self.end = int(args.f[1])
        else:
            self.start = 0
            self.end = sys.maxint

        if args.l is not None:
            self.languages = []
            for item in args.l:
                self.languages.append(item)
        else:
            self.languages = [u"Neutro", u"España"]

    def main(self):

        chapter_list = self.get_url_list_of_chapters(self.url, self.start, self.end)
        chapter_fansub_list = self.get_url_per_chapter(chapter_list, self.languages)

        item_downladed = 0

        if len(chapter_fansub_list) > 0:
            item_downladed = self.get_chapters(chapter_fansub_list, self.title, self.convert)

        return item_downladed

    def get_url_list_of_chapters(self, url, start, end):

        """
        Open the url given as argument and parse it to find all the url chapters
        that exists in McAnime.net

        Keyword arguments:
        url -- URL from McAnime of the list of chapters
            Example: "http://www.mcanime.net/enciclopedia/manga/one_piece/1223/capitulos"
        start -- Number of chapter to start downloading
        end -- Number of chapter to end downloading

        Output:
        chapter_list -- Array with tuples (number, url) that link to all the fansubs chapters.
            Example: [('0','http://www.mcanime.net/descarga_directa/manga/one_piece/1223/capitulos/0'),...]
        """
        try:
            html_reader = urllib2.urlopen(url)
        except urllib2.URLError as e:
            self.logger.debug("Error en get_url_list_of_chapters")
            self.logger.info("Dirección %s no resuelta." % url)
            return []

        html_document = html_reader.read()
        html_parser = BeautifulSoup(html_document)
        ul_list = html_parser.find_all('ul', attrs={"class": "dd_row anime_list"})
        chapter_list = []
        for element in ul_list:
            chapter_info = element.find('a')
            if start <= int(chapter_info.string) <= end:
                chapter_list.append((chapter_info.string, self.MC_DOMAIN+chapter_info['href']))

        if len(chapter_list) == 0:
            self.logger.info("No chapters found at %s with that chapter's number" % url)

        return chapter_list

    def get_url_per_chapter(self, chapter_list, languages):

        """
        Iterate throw the list of chapters to get the urls of valids chapter.

        Keyword arguments:
        chapter_list -- Array with tuples (number, url) that link to all the fansubs chapters.
            Example: [('0','http://www.mcanime.net/descarga_directa/manga/one_piece/1223/capitulos/0'),...]
        languages -- Array with the languages that can be found in McAnime and the user is looking for.
            Example: [u"Neutro", u"España"]

        Output:
        chapter_fansub_list -- Array with tuples (number, url) of valid chapters.
            Example: [('0','http://www.mcanime.net/manga_enlinea/one_piece/resonancia_de_almas_no_fansub/51014/1'),...]
        """

        chapter_fansub_list = []
        for item in chapter_list:

            try:
                html_reader = urllib2.urlopen(item[1])
            except urllib2.URLError as e:
                self.logger.debug("Error en get_url_per_chapter")
                self.logger.info("Dirección %s no resuelta." % item[1])
                return []

            html_document = html_reader.read()
            html_parser = BeautifulSoup(html_document)
            ul_list = html_parser.find_all('ul', attrs={"class": "dd_row dd_rel"})
            for element in ul_list:
                language = element.find('li', attrs={"class": "dd_type"}).find('img')['title']
                if language in languages:
                    a_element = element.find('li', attrs={"class": "dd_read"}).find('a')
                    if a_element is not None:
                        chapter_fansub_list.append((item[0], self.MC_DOMAIN+a_element['href']))
                        break

        if len(chapter_list) > 0 and len(chapter_fansub_list) == 0:
            self.logger.info("No chapters found with that languages")

        return chapter_fansub_list

    def get_chapters(self, chapter_fansub_list, title, convert):

        chapters_downloaded = 0

        for item in chapter_fansub_list:
            print item[1]
            md = MangaDownloader.MangaDownloader(item[1], title, item[0], convert)
            if md.main():
                chapters_downloaded += 1

        return chapters_downloaded

if __name__ == '__main__':

    #Usage example
    m = MangaFinder(get_arguments())
    result = m.main()
    print "Downloaded "+str(result)+" chapters"
