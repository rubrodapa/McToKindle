# -*- coding: UTF-8 -*-

import urllib2
import re
import os.path
import logging
from bs4 import BeautifulSoup
from kcc.kcc import comic2ebook
from kcc.kcc import kindlesplit
from subprocess import call
from shutil import move


class MangaDownloader():

    LOG_FILE = "log.log"


    def __init__(self, manga_url, manga_title, manga_number, convert):

        logging.basicConfig(filename=self.LOG_FILE, level=logging.DEBUG,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("MangaDownloader")

        self.manga_url = manga_url
        self.manga_title = manga_title
        self.manga_number = manga_number
        self.convert = convert

    def main(self):

            html_parser = self.open_html(self.manga_url)
            if html_parser is None:
                return False
            manga_info = self.get_pages_and_path(html_parser)

            if self.convert:

                if self.download_images(manga_info):
                    item = self.create_mobi_file(self.manga_title+"_"+self.manga_number)
                    self.clean_files(item)
                else:
                    return False
                #self.clean_mobi_file(item)
            else:
                self.download_images_to_collection(manga_info, self.manga_title, self.manga_number)

            return True

    def open_html(self, url):
        try:
            html_reader = urllib2.urlopen(url)
        except urllib2.URLError as e:
            self.logger.debug("Error in open_html")
            self.logger.info("Host %s not result" % url)
            return None
        html_document = html_reader.read()
        soup = BeautifulSoup(html_document)
        return soup


    def get_pages_and_path(self, html_parser):
        pages = len(html_parser.find('select', attrs={"name": "page"}).find_all('option'))
        complete_path = html_parser.find('div', 'current_page').find('img')['src']
        extension = os.path.splitext(complete_path)[1]
        regex = '\d+' + extension + '$'
        base_path = re.sub(regex, '', complete_path)
        return [pages, base_path, extension]

    def download_images_to_collection(self, info, title, number):

        folder = '.\collection'
        manga_dir_path = os.path.join(folder, title)

        if not os.path.isdir(manga_dir_path):
            os.makedirs(manga_dir_path)
        chapter_dir_path = os.path.join(manga_dir_path, number)
        if not os.path.isdir(chapter_dir_path):
            os.makedirs(chapter_dir_path)

        self.delete_image_files(chapter_dir_path)

        pages = info[0]
        base_path = info[1]
        extension = info[2]

        i = 0
        actual_page = i
        attemps = 0
        while i < pages:
            path = base_path + str(actual_page) + extension
            print "Downloading file: " + path
            try:
                img_file = urllib2.urlopen(path)
            except urllib2.URLError, e:
                self.logger.debug("Error in download_images_to_collection")
                self.logger.info("Host %s not result" % path)
                return False
            except urllib2.HTTPError, e:
                if e.code == 404:
                    if extension == '.jpg' and attemps == 0:
                        extension = '.png'
                        attemps += 1
                    elif extension == '.png' and attemps == 0:
                        extension = '.jpg'
                        attemps += 1
                    elif extension == '.jpg' and attemps == 1:
                        extension = '.png'
                        actual_page += 1
                        attemps += 1
                    elif extension == '.png' and attemps == 1:
                        extension = '.jpg'
                        actual_page += 1
                        attemps += 1
                    elif extension == '.jpg' and attemps == 2:
                        extension = '.png'
                        attemps += 1
                    elif extension == '.png' and attemps == 2:
                        extension = '.jpg'
                        attemps += 1
                    else:
                        self.logger.debug("Error in download_images_to_collection")
                        self.logger.info("%s gives an 404 after all the attemps" % path)
                        return False
                continue

            if i < 10:
                stri = '00' + str(i)
            elif i < 100:
                stri = '0' + str(i)
            else:
                stri = str(i)

            output_name = os.path.join(chapter_dir_path, stri + extension)
            output = open(output_name, 'wb')
            output.write(img_file.read())
            output.close()
            i += 1
            actual_page += 1

        return True

    def download_images(self, info):

        self.delete_image_files('.\images')

        pages = info[0]
        base_path = info[1]
        extension = info[2]

        i = 0
        actual_page = i
        attemps = 0
        while i < pages:
            path = base_path + str(actual_page) + extension

            try:
                img_file = urllib2.urlopen(path)
            except urllib2.URLError, e:
                self.logger.debug("Error in download_images")
                self.logger.info("Host %s not result" % path)
                return False
            except urllib2.HTTPError, e:
                if e.code == 404:
                    if extension == '.jpg' and attemps == 0:
                        extension = '.png'
                        attemps += 1
                    elif extension == '.png' and attemps == 0:
                        extension = '.jpg'
                        attemps += 1
                    elif extension == '.jpg' and attemps == 1:
                        extension = '.png'
                        actual_page += 1
                        attemps += 1
                    elif extension == '.png' and attemps == 1:
                        extension = '.jpg'
                        actual_page += 1
                        attemps += 1
                    elif extension == '.jpg' and attemps == 2:
                        extension = '.png'
                        attemps += 1
                    elif extension == '.png' and attemps == 2:
                        extension = '.jpg'
                        attemps += 1
                    else:
                        self.logger.debug("Error in download_images")
                        self.logger.info("%s gives an 404 after all the attemps" % path)
                        return False
                continue

            if i < 10:
                stri = '00' + str(i)
            elif i < 100:
                stri = '0' + str(i)
            else:
                stri = str(i)

            output_name = '.\images\\' + stri + extension
            output = open(output_name, 'wb')
            output.write(img_file.read())
            output.close()
            i += 1
            actual_page += 1

        return True

    def create_mobi_file(self, title):
        name = title + ".epub"
        title_for_comic = title.replace("_", " ")
        output_path = comic2ebook.main(['-o', name, '-q', '0', '-t', title_for_comic, '--upscale', '.\images'])
        self.delete_image_files('.\images')
        item = output_path[0]
        call(["kindlegen", item])
        return item

    def clean_mobi_file(self, item):
        mobiPath = item.replace('.epub', '.mobi')
        move(mobiPath, mobiPath + '_toclean')
        mobisplit = kindlesplit.mobi_split(mobiPath + '_toclean', True)
        open(mobiPath, 'wb').write(mobisplit.getResult())
        os.remove(mobiPath + '_toclean')
        os.remove(item)

    def clean_files(self, item):
        os.remove(item)

    def delete_image_files(self, folder):

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                self.logger.debug(e)


if __name__ == '__main__':
    #Usage example
    MangaDownloader('http://www.mcanime.net/manga_enlinea/one_piece/shinshin_fansub/518665/1#ver', 'One_Piece_731')