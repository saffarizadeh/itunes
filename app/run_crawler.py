__author__ = 'kambiz'

from app_details import AppCrawler
from review_downloader import ReviewCrawler
from review_extractor import ReviewExtractor
from app.models import *
import time
import urllib2
import socket
import requests
import gc


# app_id_list = ToCrawl.objects.filter(is_crawled=False).values_list('store_app_id', flat=True).distinct()

app_id_list = RankingsAnalytics.objects.filter(n_observations__gte=20, single_gaps__lte=1, two_cons_gaps=0, three_cons_gaps=0, four_plus_cons_gaps=0).values_list('store_app_id', flat=True).distinct()[:100]

crawled_apps = App.objects.all().values_list('store_app_id', flat=True).distinct()
# app_id_list = open('app_list_1.csv', 'r').read().split('\n')
# app_id_list = [int(app_id) for app_id in app_id_list if app_id]
# app_id_list = [app_id for app_id in app_id_list if (app_id not in crawled_apps)]


print(len(app_id_list))


NA_apps = []
app_store = 'us'
# for store_app_id in app_id_list:
#     while True:
#         print(store_app_id)
#         try:
#             app_details_crawler = AppCrawler(app_id=store_app_id, app_store=app_store)
#             created = app_details_crawler.get_app()
#             if created:
#                 app_to_crawl = ToCrawl.objects.filter(store_app_id=store_app_id)
#                 app_to_crawl.update(is_crawled=True)
#             else:
#                 NA_apps.append(store_app_id)
#             # time.sleep(1)
#         except urllib2.HTTPError as err:
#             if err.code == 503:
#                 print('503')
#                 time.sleep(360)
#                 continue
#             else:
#                 print(err)
#                 time.sleep(360)
#                 continue
#         except Exception as err:
#             print(err)
#             time.sleep(360)
#             continue
#         break
#
#
# NA_apps_file=open('NA_apps_1.txt', 'w')
# NA_apps_file.write(str(NA_apps))
# NA_apps_file.close()

app_list = App.objects.filter(is_reviews_crawled=False).order_by('total_pages')
for app in app_list:
    # print gc.collect()
    while True:
        try:
            print(app.store_app_id)
            app_reviews_crawler = ReviewCrawler(app_id=app.store_app_id, app_store=app_store)
            app_reviews_crawler.start_download()

            app_reviews_extractor = ReviewExtractor(app_id=app.store_app_id)
            """app_reviews_extractor.save_reviews() could be used to create separate tables for users and reviews"""
            app_reviews_extractor.flat_save_reviews()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 503:
                print('503')
                time.sleep(360)
                continue
            else:
                print(err, 'HTTP')
                time.sleep(360)
                continue
        except socket.timeout as err:
            print(err, 'Socket')
            time.sleep(360)
            continue
        except Exception as err:
            print(err, 'Other')
            time.sleep(360)
            continue
        break
    app.is_reviews_crawled = True
    app.save()


