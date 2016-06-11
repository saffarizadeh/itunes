# -*- coding: utf-8 -*-
import re
from lxml import etree
import urllib2
import datetime

page_number = 0
app_id = 284882215
user_agent = 'iTunes/12.3.2  (Macintosh; Intel Mac OS X 10.5.8) AppleWebKit/533.16'
store_id_d = 143441
front = "143441"
url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (app_id, page_number)
req = urllib2.Request(url, headers={"X-Apple-Store-Front": front,"User-Agent": user_agent})
u = urllib2.urlopen(req, timeout=30)
page = u.read()
# root = ET.fromstring(page)
parser = etree.XMLParser(recover=True)
root = etree.fromstring(page, parser=parser)
for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b'):
    try:
        total_pages = re.search('Page 1 of (\d+)', node.text).group(1)
    except:
        total_pages = 1
print total_pages

# from lxml import etree
#
# from pymongo import MongoClient
#
# url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (app_id, page_number)
# req = urllib2.Request(url, headers={"X-Apple-Store-Front": front,"User-Agent": user_agent})
# u = urllib2.urlopen(req, timeout=30)
# page = u.read()
# parser = etree.XMLParser(recover=True)
# root = etree.fromstring(page, parser=parser)
# page = etree.tostring(root, encoding='unicode')
# client = MongoClient()
# db = client.test
#
#
# db.itunes_test.delete_many({'store_app_id':app_id})
# cursor = db.itunes_test.find({'store_app_id':app_id})
#
# db.itunes_test.insert_one({'store_app_id':app_id,
#                         'page':page,
#                         'crawled_on': datetime.datetime.now()
#                         })
#
# cursor = db.itunes_test.find({'store_app_id':app_id})
# page = cursor[0]['page']
# parser = etree.XMLParser(recover=True)
# root = etree.fromstring(page, parser=parser)
# review_ids=[]
# for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}LoadFrameURL'):
#     review_ids.append(int(re.search('viewVote(\d+)', node.attrib['frameViewName']).group(1)))
# print review_ids


# import psycopg2
# try:
#     conn = psycopg2.connect("dbname='test1' user='postgres' host='localhost' password='linux116'")
# except:
#     print "I am unable to connect to the database"
# cur = conn.cursor()
#
# namedict = ({'store_app_id': 1, 'review_id': 5, 'title': 'gfgdf', 'body': 'gfdgdfgd',
#                    'star_rating': 4.5, 'date': '2015-04-12', 'username':'mammad',
#                    'user_apple_id': 5645, 'user_reviews_url': 'dsadasdas'})
# cur.executemany("""INSERT INTO app_reviewflat(store_app_id,review_id,title,body,star_rating,date,username,user_apple_id,user_reviews_url) VALUES (%(store_app_id)s, %(review_id)s, %(title)s, %(body)s, %(star_rating)s, %(date)s, %(username)s, %(user_apple_id)s, %(user_reviews_url)s)""", namedict)
#
#
