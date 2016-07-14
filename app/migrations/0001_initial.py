# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-14 02:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField()),
                ('appfigures_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('size', models.BigIntegerField(default=0)),
                ('current_version', models.CharField(max_length=50)),
                ('first_release_date', models.DateTimeField()),
                ('price', models.FloatField(default=0)),
                ('minimum_os_version', models.CharField(max_length=50)),
                ('user_rating_count', models.BigIntegerField(default=0)),
                ('average_user_rating', models.FloatField(default=0)),
                ('bundle_id', models.CharField(max_length=200)),
                ('total_pages', models.IntegerField(blank=True, null=True)),
                ('total_reviews', models.IntegerField(blank=True, null=True)),
                ('is_reviews_crawled', models.BooleanField(default=False)),
                ('is_releasenotes_crawled', models.BooleanField(default=False)),
                ('crawled_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AppAnnieRankings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField(default=0)),
                ('app_name', models.CharField(max_length=200)),
                ('rank_type', models.CharField(max_length=20)),
                ('category', models.CharField(max_length=200)),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('date', models.DateTimeField()),
                ('is_crawled', models.BooleanField(default=False)),
                ('crawled_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AppAnnieReleaseNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=200)),
                ('date', models.DateTimeField()),
                ('note', models.TextField(blank=True, null=True)),
                ('crawled_on', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.App')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_category_id', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PanelData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField(default=0)),
                ('category', models.CharField(max_length=200)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(max_length=20)),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('window', models.DateTimeField()),
                ('new_leadusers_cumu', models.IntegerField(blank=True, null=True)),
                ('rank_improvement', models.IntegerField(blank=True, null=True)),
                ('forward_feedback_volume', models.IntegerField(blank=True, null=True)),
                ('backward_engagement_pos', models.IntegerField(blank=True, null=True)),
                ('backward_engagement_neg', models.IntegerField(blank=True, null=True)),
                ('version_cumu_volume', models.IntegerField(blank=True, null=True)),
                ('total_cumu_volume', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RankingsAnalytics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField(default=0)),
                ('category', models.CharField(max_length=200)),
                ('rank_type', models.CharField(max_length=20)),
                ('first_appearance', models.IntegerField(blank=True, null=True)),
                ('last_appearance', models.IntegerField(blank=True, null=True)),
                ('n_observations', models.IntegerField(blank=True, null=True)),
                ('n_gaps', models.IntegerField(blank=True, null=True)),
                ('mean_gap', models.FloatField(blank=True, null=True)),
                ('std_gap', models.FloatField(blank=True, null=True)),
                ('gaps', models.CharField(max_length=200)),
                ('mean_rank', models.FloatField(blank=True, null=True)),
                ('std_rank', models.FloatField(blank=True, null=True)),
                ('min_rank', models.IntegerField(blank=True, null=True)),
                ('max_rank', models.IntegerField(blank=True, null=True)),
                ('single_gaps', models.IntegerField(blank=True, null=True)),
                ('two_cons_gaps', models.IntegerField(blank=True, null=True)),
                ('three_cons_gaps', models.IntegerField(blank=True, null=True)),
                ('four_plus_cons_gaps', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=200)),
                ('date', models.DateTimeField()),
                ('note', models.TextField(blank=True, null=True)),
                ('crawled_on', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.App')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewFlat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField()),
                ('appfigures_id', models.IntegerField(blank=True, null=True)),
                ('review_id', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=400)),
                ('body', models.TextField(blank=True, null=True)),
                ('star_rating', models.IntegerField(default=0)),
                ('date', models.DateTimeField()),
                ('username', models.CharField(max_length=200)),
                ('user_apple_id', models.IntegerField(default=0)),
                ('user_reviews_url', models.URLField(blank=True, null=True)),
                ('crawled_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewReleaseNoteFlat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField()),
                ('is_review', models.BooleanField(default=True)),
                ('review_id', models.IntegerField(default=0)),
                ('body', models.TextField(blank=True, null=True)),
                ('star_rating', models.IntegerField(default=0)),
                ('username', models.CharField(blank=True, max_length=200, null=True)),
                ('user_apple_id', models.IntegerField(default=0)),
                ('user_reviews_url', models.URLField(blank=True, null=True)),
                ('version', models.CharField(blank=True, max_length=200, null=True)),
                ('date', models.DateTimeField()),
                ('crawled_on', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ReviewReleaseNoteSim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_app_id', models.IntegerField()),
                ('star_rating', models.IntegerField(default=0)),
                ('user_apple_id', models.IntegerField(default=0)),
                ('version', models.CharField(blank=True, max_length=200, null=True)),
                ('date', models.DateTimeField()),
                ('word_count', models.IntegerField(default=0)),
                ('similarity', models.FloatField(default=0)),
                ('releasenote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='releasenote', to='app.ReviewReleaseNoteFlat')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='app.ReviewReleaseNoteFlat')),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_seller_id', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='app',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Category'),
        ),
        migrations.AddField(
            model_name='app',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Seller'),
        ),
    ]
