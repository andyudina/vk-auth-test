#coding: utf-8

from django.db import models
from django.contrib.auth.models import User

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import hashlib, binascii
import base64
import sys

from pyDes import *

from vk_oauth.settings import KEY


class TRIPLEDESEncryptor:
    def __init__(self, key):
        self.key = key

    def generate_hash(self, salt):   
        return hashlib.pbkdf2_hmac('sha256', self.key, salt, 1000000, 24)
 
    def encrypt(self, data, salt):
        key = self.generate_hash(salt)
        cipher = triple_des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
        encoded_data = data.decode('utf-8').encode('ascii')
        return cipher.encrypt(encoded_data)

    def decrypt(self, data, salt):
        key = self.generate_hash(salt)
        cipher = triple_des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
        return cipher.decrypt(data)
 

class EncryptedCharField(models.CharField):
    def __init__(self, encryptor, *args, **kwargs):
        super(EncryptedCharField, self).__init__(*args, **kwargs)
        self.encryptor = encryptor

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        else:
            salt, val = value.split('#')
            val =  binascii.a2b_base64(val).encode('hex_codec')
            access_token = self.encryptor.decrypt(val.decode('hex_codec'), salt)
            return access_token#VkUser.salt_access_token(salt, access_token)
        
    
    def get_prep_value(self, value):
        if value is None:
            return value
        else:
            salt, val = value.split('#')
            access_token = self.encryptor.encrypt(val, salt)
            access_token = binascii.b2a_base64(access_token)
            return VkUser.salt_access_token(salt, access_token)

    def to_python(self, value):
        if value.find('#') == -1:
            return value

        if value is None:
            return value

        return value.split('#')[-1]

class VkUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = EncryptedCharField(encryptor=TRIPLEDESEncryptor(KEY), max_length=1000)
    sex = models.NullBooleanField(null=True, blank=True)#True - woman, False - man, Null-unknown
    city = models.CharField(max_length=1000, null=True, blank=True)
    bdate = models.DateField(null=True, blank=True)
    photo = models.FilePathField(path=BASE_DIR +'/images', null=True, blank=True)

    @staticmethod
    def salt_access_token(salt, token):
        return salt + '#' + token

    def save(self, *args, **kwargs):
        #print self.access_token
        if self.access_token.find('#') == -1:
            self.access_token=VkUser.salt_access_token(self.user.username, self.access_token)
        super(VkUser, self).save(*args, **kwargs)
        self.access_token = self.access_token.split('#')[-1]
        

#    pass
