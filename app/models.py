from django.db import models

class Category(models.Model):
    store_category_id = models.IntegerField()
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.id

class Seller(models.Model):
    store_seller_id = models.IntegerField()
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.id

class App(models.Model):
    store_app_id = models.IntegerField()
    appfigures_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    seller = models.ForeignKey(Seller)
    category = models.ForeignKey(Category)
    size = models.BigIntegerField(default=0)
    current_version = models.CharField(max_length=50)
    first_release_date = models.DateTimeField()
    price = models.FloatField(default=0)
    minimum_os_version = models.CharField(max_length=50)
    user_rating_count = models.BigIntegerField(default=0)
    average_user_rating = models.FloatField(default=0)
    bundle_id = models.CharField(max_length=200)
    total_pages = models.IntegerField(blank=True, null=True)
    total_reviews = models.IntegerField(blank=True, null=True)

    is_reviews_crawled = models.BooleanField(default=False)
    crawled_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id

class ReleaseNote(models.Model):
    app = models.ForeignKey(App)
    version = models.CharField(max_length=200)
    date = models.DateTimeField()
    note = models.TextField(blank=True, null=True)

    crawled_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id

#--------------------------------------------------------#
class Ranking(models.Model):
    app = models.ForeignKey(App) #category is included in app
    type = models.CharField(max_length=20) #free, paid, grossing
    rank = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()

    crawled_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id

class Rating(models.Model):
    app = models.ForeignKey(App)
    date = models.DateTimeField()
    five_stars = models.BigIntegerField(default=0)
    four_stars = models.BigIntegerField(default=0)
    three_stars = models.BigIntegerField(default=0)
    two_stars = models.BigIntegerField(default=0)
    one_stars = models.BigIntegerField(default=0)

    crawled_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id

class User(models.Model):
    username = models.CharField(max_length=200)
    user_apple_id = models.BigIntegerField(default=0)
    user_reviews_url = models.URLField(blank=True, null=True)
    # We could use an M2M structure to connect reviews to users;
    # but for the sake of simplicity we didn't use it.
    def __unicode__(self):
        return self.id

class Review(models.Model):
    app = models.ForeignKey(App)
    appfigures_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User)
    review_id = models.BigIntegerField(default=0)
    title = models.CharField(max_length=400)
    body = models.TextField(blank=True, null=True)
    star_rating = models.IntegerField(default=0)
    date = models.DateTimeField()

    crawled_on = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.id
class ReviewFlat(models.Model):
    store_app_id = models.IntegerField()
    appfigures_id = models.IntegerField(blank=True, null=True)
    review_id = models.IntegerField(default=0)
    title = models.CharField(max_length=400)
    body = models.TextField(blank=True, null=True)
    star_rating = models.IntegerField(default=0)
    date = models.DateTimeField()
    username = models.CharField(max_length=200)
    user_apple_id = models.IntegerField(default=0)
    user_reviews_url = models.URLField(blank=True, null=True)

    crawled_on = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.id

class ReviewReleaseNoteFlat(models.Model):
    store_app_id = models.IntegerField()
    is_review = models.BooleanField(default=True)

    review_id = models.IntegerField(default=0)
    body = models.TextField(blank=True, null=True)
    star_rating = models.IntegerField(default=0)
    username = models.CharField(max_length=200, blank=True, null=True)
    user_apple_id = models.IntegerField(default=0)
    user_reviews_url = models.URLField(blank=True, null=True)

    version = models.CharField(max_length=200, blank=True, null=True)

    date = models.DateTimeField()

    crawled_on = models.DateTimeField()
    def __unicode__(self):
        return self.id

class ReviewReleaseNoteSim(models.Model):
    store_app_id = models.IntegerField()
    releasenote = models.ForeignKey(ReviewReleaseNoteFlat, related_name='releasenote')
    review = models.ForeignKey(ReviewReleaseNoteFlat, related_name='review')
    star_rating = models.IntegerField(default=0)
    user_apple_id = models.IntegerField(default=0)
    version = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField()
    word_count = models.IntegerField(default=0)
    similarity = models.FloatField(default=0)
    def __unicode__(self):
        return self.id

class ToCrawl(models.Model):
    store_app_id = models.BigIntegerField(default=0)
    name = models.CharField(max_length=200, default='-')
    rank_type = models.CharField(max_length=20)
    rank = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()

    is_crawled = models.BooleanField(default=False)
    def __unicode__(self):
        return self.id

class AppAnnieRankings(models.Model):
    store_app_id = models.IntegerField(default=0)
    app_name = models.CharField(max_length=200)
    rank_type = models.CharField(max_length=20)
    category = models.CharField(max_length=200)
    rank = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()

    is_crawled = models.BooleanField(default=False)
    crawled_on = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.id