from django.db import models

# Create your models here.

class User(models.Model):

    email = models.CharField(max_length=200, blank=True)

    # sms-entry
    user_id = models.CharField(max_length=200)
    mobile = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    namespace = models.CharField(max_length=200)
    confirmation_hash = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    href = models.CharField(max_length=200)
    target_id = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    updated_at = models.DateTimeField()

    # sms-verify
    access_token = models.CharField(max_length=200)
    client_id = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    endpoints_http = models.CharField(max_length=200)
    endpoints_mqtt = models.CharField(max_length=200)
    endpoints_uploader = models.CharField(max_length=200)
    expires_at = models.DateTimeField(blank=True)
    grant_type = models.CharField(max_length=200)
    href = models.CharField(max_length=200)
    owner_id = models.CharField(max_length=200)
    refresh_token = models.CharField(max_length=200)
    scope_1 = models.CharField(max_length=200)
    scope_2 = models.CharField(max_length=200)

class Coverage(models.Model):

    name = models.CharField(max_length=200)
    user_id = models.IntegerField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200, blank=True, null = True)
    company_id = models.IntegerField(null = True)
    start_at = models.DateTimeField(blank=True, null = True)
    end_at = models.DateTimeField(blank=True, null = True)
    video_mile = models.CharField(max_length=200, blank=True, null = True)
    video_vehicle = models.CharField(max_length=200, blank=True, null = True)
    state = models.IntegerField(blank=True, null = True)   # COVERED: 1, UNCOVERED: 2
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Company(models.Model):

    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200, blank=True, null = True)
    icon_url = models.CharField(max_length=200, blank = True, null = True)
    price_per_year = models.FloatField(null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Claim(models.Model):

    name = models.CharField(max_length=200)
    user_id = models.IntegerField()
    coverage_id = models.IntegerField()
    what_happened = models.CharField(max_length=200)
    date_time_happened = models.DateTimeField()
    time_happened = models.BigIntegerField()
    latitude = models.FloatField(blank=True, null = True)
    longitude = models.FloatField(blank = True, null = True)
    address = models.CharField(max_length=200, blank = True, null = True)
    damaged_part = models.IntegerField()
    video = models.CharField(max_length=200, blank = True, null = True)
    note = models.CharField(max_length=200, blank = True, null = True)
    state = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Payment(models.Model):

    user_id = models.IntegerField()
    amount = models.IntegerField()
    currency = models.CharField(max_length=200)
    state = models.IntegerField(null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class History(models.Model):

    user_id = models.IntegerField()
    type = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

