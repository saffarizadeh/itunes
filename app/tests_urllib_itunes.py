# -*- coding: utf-8 -*-
import re
from lxml import etree
import datetime
import requests


page_number = 0
app_id = 828966363
user_agent = 'iTunes/12.3.2  (Macintosh; Intel Mac OS X 10.5.8) AppleWebKit/533.16'
app_store = 'us'
front = "143441"
url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (app_id, page_number)
headers={"X-Apple-Store-Front": front,"User-Agent": user_agent}
# u = requests.get(url, timeout=30, verify=False, headers=headers)
# page = u.content
# parser = etree.XMLParser(recover=True)
# root = etree.fromstring(page, parser=parser)
# for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b'):
#     try:
#         total_pages = re.search('Page 1 of (\d+)', node.text).group(1)
#     except:
#         total_pages = 1
# print total_pages



def extract_release_notes(page):
    # print page
    text = re.search('"versionHistory":(.+)', page).group(1).replace('null', '""').replace('true', '""')
    # print "\n\n\n\n\n\n\n\n\n\n"
    # print text
    # text = text[text.find('[{'): text.find('}]') + 2]
    try:
        t1 = text[text.find('[{"releaseNotes"'): text.rfind('"releaseNotes"') - 2]
        tm = text[text.rfind('"releaseNotes"') - 2:]
        t2 = tm[tm.find('{"releaseNotes"'):tm.find('}')+1]
        text = t1 + ',' + t2 + ']'
        releases = eval(text)
    except:
        t2 = text[text.find('{"releaseNotes"'):text.find('}') + 1]
        text = '[' + t2 + ']'
        releases = eval(text)
    release_notes = []
    for release in releases:
        release_date = datetime.datetime.strptime(release['releaseDate'], '%Y-%m-%dT%H:%M:%SZ')
        # release_note = release['releaseNotes'].decode('raw_unicode_escape') #alleviate bullet point render problem
        release_note = release['releaseNotes']
        release_version = release['versionString']
        release_notes.append({'version': release_version, 'date': release_date, 'note': release_note})
    return release_notes



app_url = "https://itunes.apple.com/%s/app/id%d?mt=8" %(app_store, app_id)
u = requests.get(app_url, timeout=30, verify=False, headers={"User-Agent": user_agent})
page = u.content
print(extract_release_notes(page))


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
