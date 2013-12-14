# -*- coding: UTF-8 -*-

import xml.etree.ElementTree as et
import logging
from email import MIMEBase
from email import MIMEMultipart
from email import MIMEText
from email import Utils
from email import Encoders
from MangaFinder import MangaFinder
import smtplib
import os


class Arguments():

    def __init__(self, url, title, number):
        self.url = url
        self.title = title
        self.k = True
        self.n = number
        self.l = None
        self.f = None


class McToKindle():

    LOG_FILE = 'log.log'

    def __init__(self):

        logging.basicConfig(filename=self.LOG_FILE, level=logging.DEBUG,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("McToKindle")

        self.configuration_tree = et.parse('manga_getter.conf')

    def main(self):
        root = self.configuration_tree.getroot()
        mangas = root.findall('manga')

        for manga in mangas:
            last_chapter = manga.find('last_chapter').text
            actual_chapter = int(last_chapter) + 1
            args = Arguments(manga.find('url').text, manga.find('title').text, [str(actual_chapter)])
            m = MangaFinder(args)
            manga_converted = m.main()

            if manga_converted == 1:
                try:
                    self.send_manga_throw_email(manga.find('title').text, actual_chapter)
                    self.send_email_notification(manga.find('title').text, actual_chapter)
                except Exception, e:
                    self.logger.warning(e.message)
                    continue
                manga.find('last_chapter').text = str(actual_chapter)
                self.configuration_tree.write("manga_getter.conf")

    def send_manga_throw_email(self, title, number):
        """
        This function sends an email using Gmail SMTP Server to the kindle cloud with the
        comic attached into it.

        Keyword arguments:
        title - The title of the manga
        number - The chapter number of the manga
        """
        msg = MIMEMultipart.MIMEMultipart()
        msg['from'] = "from@gmail.com"
        msg['To'] = "to@kindle.com"
        msg['Date'] = Utils.formatdate(localtime=True)
        msg['Subject'] = ''

        msg.attach(MIMEText.MIMEText(''))

        part = MIMEBase.MIMEBase('application', "octet-stream")
        filename = title+"_"+str(number)+".mobi"
        part.set_payload(open(filename, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login("from@gmail.com", "xxxpasswordxxx")
        smtp.sendmail("from@gmail.com", "to@kindle.com", msg.as_string())
        smtp.close()

    def send_email_notification(self, title, number):
        """
        This function sends an email using Gmail SMTP Server to any email with a message telling that
        the manga has been sent to the kindle cloud.

        Keyword arguments:
        title - The title of the manga
        number - The chapter number of the manga
        """
        msg = MIMEMultipart.MIMEMultipart()
        msg['from'] = "from@gmail.com"
        msg['To'] = "to@gmail.com"
        msg['Date'] = Utils.formatdate(localtime=True)
        msg['Subject'] = 'Manga %s %s notification' % (title, number)

        msg.attach(MIMEText.MIMEText('The chapter number %s of manga %s has been sent to '
                                     'the kindle cloud' % (number, title)))

        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login("from@gmail.com", "xxxpasswordxxx")
        smtp.sendmail("from@gmail.com", "to@gmail.com", msg.as_string())
        smtp.close()

if __name__ == '__main__':

    #The log file is not going to be bigger than 1MB
    if os.path.isfile('log.log'):
        size = os.stat('log.log').st_size
        if size > 1048576:
            os.remove('log.log')
            open('log.log', 'w').close()

    w = McToKindle()

    try:
        w.main()
    except Exception, e:
        w.logger.warning(e.message)