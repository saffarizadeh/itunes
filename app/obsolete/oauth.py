# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

from rauth import OAuth1Session, OAuth1Service
from StringIO import StringIO
import json
import datetime
from app.models import *

base_url = "https://api.appfigures.com/v2"
client_key = "4d843d3ed89c4a478f8c2f5db18ea94f"
client_secret = "fb20d3adccca41baae5845914d7836e0"


request_token_url = base_url + "/oauth/request_token"
authorize_url = base_url + "/oauth/authorize"
access_token_url = base_url + "/oauth/access_token"

def get_service():
  """ Returns an OAuthService configured for us """
  return OAuth1Service(name="appfigures",
                        consumer_key=client_key,
                        consumer_secret=client_secret,
                        request_token_url=request_token_url,
                        access_token_url=access_token_url,
                        authorize_url=authorize_url,
                        base_url=base_url)


def get_session(access_token=None, access_token_secret=None):
  """If access_token and secret are given, create and return a session.

      If they are not given, go through the authorization process
      interactively and return the new session
  """
  oauth = get_service()

  if access_token:
    session = OAuth1Session(client_key, client_secret,
                            access_token, access_token_secret,
                            service=oauth)
    return session

  params = {"oauth_callback": "oob"}
  headers = {'X-OAuth-Scope': 'public:read,products:read'}
  request_token, request_token_secret = oauth.get_request_token(
                                          params=params,
                                          headers=headers
                                        )

  authorization_url = oauth.get_authorize_url(request_token)
  print("Go here: %s to get your verification token."
          % authorization_url)
  verifier = raw_input("Paste verifier here: ")
  session =  oauth.get_auth_session(request_token,
                                    request_token_secret,
                                    "POST",
                                    data={"oauth_verifier":verifier})
  return session


class RankingDownloader(object):
    def __init__(self, session, category):
        self.session = session
        self.category = category
        self.rank_type_list = ['free', 'paid', 'topgrossing']
        current_date = datetime.datetime.now()
        self.date_list = ['2016-01-06']

    def get_ranking(self):
        apps=[]
        for date in self.date_list:
            for rank_type in self.rank_type_list:
                url = base_url + "/ranks/snapshots/"+date+"/us/"+str(category)+"/"+rank_type
                resp = self.session.get(url)
                rank = 0
                for response in resp.json().items()[3][1]:
                    rank += 1
                    print datetime.datetime.strptime(date, "%Y-%m-%d")
                    apps.append({'rank':rank,
                                'rank_type':rank_type,
                                'date': datetime.datetime.strptime(date, "%Y-%m-%d"),
                                'store_app_id': response['ref_no'],
                                'name': response['name'],
                                'appfigures_id': response['id']})
        return apps

    def create_ranking(self, store_app_id, name, rank_type, rank, date):
        try:
            app = ToCrawl.objects.get(store_app_id=store_app_id,
                                      rank_type=rank_type,
                                      date=date)
        except:
            app = ToCrawl.objects.create(store_app_id=store_app_id,
                                         name=name,
                                         rank_type=rank_type,
                                         rank=rank,
                                         date=date)
        return app

    def run(self):
        apps = self.get_ranking()
        for app in apps:
            self.create_ranking(store_app_id=app['store_app_id'],
                                name=app['name'][0:200],
                                rank_type=app['rank_type'],
                                rank=app['rank'],
                                date=app['date'])


session = get_session('9XFnPucBSexloMZ3', 'jY7KSYHeq3hn6U1L')
print("Access Token: %s\tAccess Secret:%s"
      % (session.access_token, session.access_token_secret))
category = 25204
ranking_downloader = RankingDownloader(session=session, category=category)
ranking_downloader.run()
