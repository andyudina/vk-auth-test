#coding: utf-8
from django.db import models
from django.contrib.auth.models import User

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class VkUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=4000)
    sex = models.NullBooleanField(null=True, blank=True)#True - woman, False - man, Null-unknown
    city = models.CharField(max_length=1000, null=True, blank=True)
    bdate = models.DateField(null=True, blank=True)
    photo = models.FilePathField(path=BASE_DIR +'/images', null=True, blank=True)
# Create your models here.

#class EncryptedCharField(models.CharField):
#    def __init__(self, *args, **kwargs):
#        super(EncryptedCharField, self).__init__(*args, **kwargs)
#
#    def to_python(self, value):
    