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
import xlsxwriter
import numpy
from datetime import datetime

def count_words(document):
    words = note.split()
    count = len(words)
    return count


NA_apps = []
row_num = 0
period_start_date = datetime.strptime('2014-01-01', '%Y-%m-%d')

workbook = xlsxwriter.Workbook('rn_app_list_1.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write(row_num, 0, 'store_app_id')
worksheet.write(row_num, 1, 'first_release_date')
worksheet.write(row_num, 2, 'first_release_note_date')
worksheet.write(row_num, 3, 'gap_from_fr_or_2014')
worksheet.write(row_num, 4, 'release_notes_count')
worksheet.write(row_num, 5, 'nonempty_release_notes_count')
worksheet.write(row_num, 6, 'app_words_count')
worksheet.write(row_num, 7, 'mean_word_count')
worksheet.write(row_num, 8, 'std_word_count')
worksheet.write(row_num, 9, 'min_word_count')
worksheet.write(row_num, 10, 'max_word_count')
worksheet.write(row_num, 11, 'word_count_list')

app_id_list = open('app_list_1.csv', 'r').read().split('\n')
for store_app_id in app_id_list:
    try:
        app = App.objects.get(store_app_id=store_app_id)
        release_notes = ReleaseNote.objects.filter(app=app).order_by('date')
        first_release_note_date = release_notes.earliest('date').date
        first_release_date = app.first_release_date
        if first_release_date > period_start_date:
            gap = (first_release_note_date - first_release_date).days + 1
        else:
            gap = (first_release_note_date - datetime.strptime('2014-01-01', '%Y-%m-%d')).days + 1
        if gap<0:
            gap = 0
        gap_from_fr_or_2014 = gap
        '''Indicates the number of days that we are missing;
        but in our analysis we don't need release notes from
        the beginning of period because we want to find the
        impact of reviews on future release notes
        '''

        release_notes_count = release_notes.count()
        app_words_count = 0
        word_counts = []
        for release_note in release_notes:
            note = release_note.note
            if note:
                word_count = count_words(document=note)
                app_words_count += word_count
                word_counts.append(word_count)
        nonempty_release_notes_count = len(word_counts)
        mean_word_count = numpy.mean(word_counts)
        std_word_count = numpy.std(word_counts)
        min_word_count = min(word_counts)
        max_word_count = max(word_counts)

        row_num += 1
        worksheet.write(row_num, 0, app.store_app_id)
        worksheet.write(row_num, 1, app.first_release_date.strftime('%Y/%m/%d'))
        worksheet.write(row_num, 2, first_release_note_date.strftime('%Y/%m/%d'))
        worksheet.write(row_num, 3, gap_from_fr_or_2014)
        worksheet.write(row_num, 4, release_notes_count)
        worksheet.write(row_num, 5, nonempty_release_notes_count)
        worksheet.write(row_num, 6, app_words_count)
        worksheet.write(row_num, 7, mean_word_count)
        worksheet.write(row_num, 8, std_word_count)
        worksheet.write(row_num, 9, min_word_count)
        worksheet.write(row_num, 10, max_word_count)
        worksheet.write(row_num, 11, str(word_counts))
    except:
        NA_apps.append(store_app_id)
workbook.close()

NA_apps_file=open('rn_NA_apps_1.txt', 'w')
NA_apps_file.write(str(NA_apps))
NA_apps_file.close()