from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from models import VkUser
import json
import re
import requests
import datetime
from vk_oauth.settings import STATIC_URL
from django.http import Http404, HttpResponse
# Create your views here.
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VK_OAUTH_URL = 'https://oauth.vk.com/authorize?client_id={client_id}&display=page&redirect_uri={uri}&scope={scope}&response_type=token&v=5.37'.format(client_id='5042170', 
                                           uri='http://localhost:8000', 
                                           scope=','.join(['offline', 'groups']))

VK_API_BASE_URL = 'https://api.vk.com/method/{METHOD_NAME}?{PARAMETERS}'

def big_login_button(request):
    if request.method == "POST":
        if 'login' in request.POST:
            return redirect(VK_OAUTH_URL)
    return render(request, 'vk_auth/login.html')

def login(request):
    try: 
        fragment = request.GET['fragment']
        pattern = re.compile("access_token=([a-zA-Z0-9]+)&expires_in=([0-9]+)&user_id=([0-9]+)")
        result = pattern.match(fragment)
        user_id = result.group(3)
        access_token = result.group(1)
        if not user_id or not access_token:
            raise Exception
    except Exception as e:
        print 'login| fragment', e
        return HttpResponse(json.dumps({'result': False}))

    try:
        user = User.objects.get(username=user_id)
        if not user:
            raise User.DoesNotExist
        if not user.vkuser:
            user.vkuser = VkUser.objects.create(access_token=VkUser.salt_access_token(user_id, access_token),
                                                user=user)
        user.vkuser.access_token = VkUser.salt_access_token(user_id, access_token)
        user.vkuser.save()
    except Exception as e:
        print 'login| get user', e
        user = User.objects.create_user(username=user_id, password=user_id)   
        try:
            user.vkuser = VkUser.objects.create(access_token=VkUser.salt_access_token(user_id, access_token),
                                                user=user)
        except Exception as e:
            print 'login| get vkuser', e
    user = authenticate(username=user_id, password=user_id)
    auth_login(request, user)
    return HttpResponse(json.dumps({'result': True}))


def logout(request):
    if request.user.is_authenticated():
        update_user_info(request.user)
        griups = None
        try:
             groups = get_all_vk_groups(request.user, groups_parse)
        except Exception as e:
            print 'groups err:', e
        if request.method == "POST":
            if 'logout' in request.POST:
                auth_logout(request)
                return redirect('login_button')
        return render(request, 'vk_auth/login_success.html', {'photo': request.user.vkuser.photo, 'groups': groups})
    else:
        return redirect('login_button')

def update_user_info(user):
    try:
        user_info = get_user_info(user, user_parse)
    except Exception as e:
        print 'update_user_info', e
        return

    user.last_name = user_info['last_name']
    user.first_name = user_info['first_name']
    if 'sex' in user_info:
        user.vkuser.sex = user_info['sex']
    if 'bdate' in user_info:
        user.vkuser.bdate = user_info['bdate']
    if 'city' in user_info:
        user.vkuser.city = user_info['city']
    if 'photo' in user_info:
        user.vkuser.photo = user_info['photo'] 

    user.vkuser.access_token
    user.vkuser.save()
       

def get_user_info(user, user_parse):
    url = generate_vk_url('users.get', {'user_id':user.username,
                                        'fields': 'sex, bdate, city, photo_max',
                                        'access_token': user.vkuser.access_token})
    #print user.vkuser.access_token
    vk_response = requests.get(url)
    vk_json = vk_response.json()
    return user_parse(vk_json)
        
def user_parse(vk_json):
    info = vk_json['response'][0]
    person_info = {'first_name': info['first_name'],
                   'last_name': info['last_name']}
    try:
        city = get_info_from_vk_database('database.getCitiesById', { 'city_ids' : str(info['city'])
                                                                   }, 'name')
        person_info['city'] = city
    except Exception as e:
        print 'user_parse|city', e
        pass

    try:
        photo_url = info['photo_max']
        file_name = photo_url.split('/')[-1]
        photo_response = requests.get(photo_url, stream=True)
        if photo_response.status_code == 200:
            file_name = STATIC_URL + 'vk_auth/images/' + file_name
            file_path = '/vk_auth'  + file_name
            with open(BASE_DIR + file_path, 'wb+') as photo_file:
                for chunk in photo_response.iter_content(1024):
                    photo_file.write(chunk) 
                photo_file.close()
            person_info['photo'] = file_name
    except Exception as e:
        print 'user_parse|photo', e
        pass

    try:
        #print info['bdate']
        date, month, year = info['bdate'].split('.')
        #print date, month, year
        person_info['bdate'] = datetime.date(int(year), int(month), int(date))
    except Exception as e:
        #print 'user_parse|date', e
        pass

    try:
        person_info['sex'] = info['sex']
        if person_info['sex'] == 2:
            person_info['sex'] = False
        elif person_info['sex'] == 1:
            person_info['sex'] = True
        else:
            person_info['sex'] = None
    except Exception as e:
        print 'user_parse|gender', e
        pass

    return person_info

def generate_vk_url(method, params_dict):
    params = '&'.join(['='.join([key, val]) for key, val in params_dict.iteritems()])
    return VK_API_BASE_URL.format(METHOD_NAME=method, 
                                  PARAMETERS=params)

def get_info_from_vk_database(method, params, field):
    url = generate_vk_url(method, params)
    vk_response = requests.get(url)
    return vk_response.json()['response'][0][field]

def get_all_vk_groups(user, groups_parse):
    url = generate_vk_url('groups.get', {'user_id':user.username,
                                         'filter': 'moder',
                                         'extended' : '1',
                                         'access_token': user.vkuser.access_token})
    #print url
    vk_response = requests.get(url)
    return groups_parse(vk_response.json())

def groups_parse(vk_json):
    print vk_json
    group_items = vk_json['response'][1:]
    result_groups = []
    for group in group_items:
        result_groups.append((group['gid'], group['name']))
    return result_groups

#enciphering sould be done inside object manager!!
#def cipher_acces_token(user_id, access_token):
#    return access_token
