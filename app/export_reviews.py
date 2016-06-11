from __future__ import print_function
# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()
from app.models import *
import pickle

app_ids = [307906541, 282614216, 383298204, 421254504, 509993510]

apps = {}
for app in App.objects.all():
  release_notes = ReleaseNote.objects.filter(app=app).order_by('date')
  release_notes = [rn.note for rn in release_notes]
  reviews = ReviewFlat.objects.filter(store_app_id=app.store_app_id).order_by('date')
  reviews = [review.body for review in reviews]
  apps[app.store_app_id] = {'release_notes': release_notes, 'reviews': reviews}

pickle.dump( apps, open( "apps.p", "wb" ) )
