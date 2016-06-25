__author__ = 'Kambiz'
import urllib2
import xml.etree.ElementTree as ET
from lxml import etree
import re
import os
import time
from pymongo import MongoClient
import datetime




class ReviewCrawler(object):
    def __init__(self, app_id, app_store):
        self.app_id = app_id
        self.app_store = app_store
        self.start_page = 0
        self.front = '143441'
        self.total_pages = 0  ################start from 0 or 1???
        self.finish_page = 0
        self.user_agent = 'iTunes/12.3.2  (Macintosh; Intel Mac OS X 10.5.8) AppleWebKit/533.16'
        # if not os.path.exists('xml/' + str(self.app_id)):
        #     os.makedirs('xml/' + str(self.app_id))
        self.xml_folder = 'xml/' + str(self.app_id) + '/'
        self.tmp_folder = 'tmp/'
        self.client = MongoClient()
        self.db = self.client.test

    def get_total_pages(self):
        page_number = 0
        url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (self.app_id, page_number)
        req = urllib2.Request(url, headers={"X-Apple-Store-Front": self.front,"User-Agent": self.user_agent})
        u = urllib2.urlopen(req, timeout=5)
        page = u.read()
        # root = ET.fromstring(page)
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(page, parser=parser)
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b'):
            try:
                self.total_pages = re.search('Page 1 of (\d+)', node.text).group(1)
            except:
                self.total_pages = 1
        self.total_pages = int(self.total_pages)
        self.finish_page = self.total_pages

    def download_reviews(self):
        for page_number in range(self.start_page,self.finish_page):
            url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (self.app_id, page_number)
            req = urllib2.Request(url, headers={"X-Apple-Store-Front": self.front,"User-Agent": self.user_agent})
            u = urllib2.urlopen(req, timeout=5)
            page = u.read()
            parser = etree.XMLParser(recover=True)
            page = etree.fromstring(page, parser=parser)
            page = etree.tostring(page, encoding='unicode')



            self.db.itunes.insert_one({'store_app_id':self.app_id,
                                    'page':page,
                                    'crawled_on': datetime.datetime.now()
                                    })

            # with open(self.xml_folder +str(page_number)+'.xml', 'w') as file_:
            #     file_.write(page)

            with open(self.tmp_folder+'lastpage.txt', 'w') as file_:
                file_.write(str(page_number))
            with open(self.tmp_folder+'lastapp.txt', 'w') as file_:
                file_.write(str(self.app_id))

    def chunk_download(self, chunk_size):
        """
        later it could be used for parallel connections
        """
        while True:
            self.finish_page = self.start_page + chunk_size
            if self.finish_page >= self.total_pages:
                self.finish_page = self.total_pages
            self.download_reviews()

            self.start_page = self.finish_page
            if self.finish_page >= self.total_pages:
                break
            time.sleep(5)

    def complete_last_thread(self):
        new_app_id = self.app_id
        if os.path.isfile(self.tmp_folder+'lastapp.txt'):
            self.app_id = int(open(self.tmp_folder+'lastapp.txt', 'r').read())
            self.start_page = int(open(self.tmp_folder+'lastpage.txt', 'r').read()) + 1
            self.get_total_pages()
            self.chunk_download(chunk_size=5000)
            os.remove(self.tmp_folder+'lastpage.txt')
            os.remove(self.tmp_folder+'lastapp.txt')
            needed_complete_last_thread = True
        else:
            needed_complete_last_thread = False
        self.__init__(new_app_id, self.app_store)
        return needed_complete_last_thread

    def start_download(self):
        needed_complete_last_thread = self.complete_last_thread() #if interrupted
        # The problem is that after finishing the interrupted thread, we re-download it again from the beginning
        # Also the complete_last_thread sometimes re-downloads the last page and makes a duplicate
        if not needed_complete_last_thread:
            self.get_total_pages()
            self.db.itunes.delete_many({'store_app_id':self.app_id}) #remove previously added pages for this ID
            self.chunk_download(chunk_size=5000)
            os.remove(self.tmp_folder+'lastpage.txt')
            os.remove(self.tmp_folder+'lastapp.txt')
        # self.client.close()

