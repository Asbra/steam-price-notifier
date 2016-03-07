#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author:  Johan/Asbra.net
# @Date:    2015-10-27 22:18:35
# @Email:   johan@asbra.net
# @Last modified by:   Johan/Asbra.net
# @Last modified time: 2016-03-07T07:07:39+07:00

# Imports
from os import path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import json
import requests

# Config
config = {
    'region': 'th',
    'steamid': 'novoc',
    'currency': '฿',
    'mail_from': 'steam@asbra.net',
    'mail_to': 'johan@asbra.net',
}


def email_alert(subject, text, html=None):
    global config
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['mail_from']
    msg['To'] = config['mail_to']

    if text is not None:
        msg.attach(MIMEText(text, 'plain'))
    if html is not None:
        msg.attach(MIMEText(html, 'html'))

    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
    except Exception, e:
        print str(e)


# Truncate log file
f = open('_log.txt', 'w')
f.close()

# Config
store_url = 'https://store.steampowered.com'
app_url = store_url + '/app/%s/'
my_url = 'https://steamcommunity.com/id/%s' % config['steamid']

# Get wishlist
r = requests.get('%s/wishlist' % my_url)
wishlist = re.findall(r'id="game_([0-9]+)"', r.text)

# Get followed games
r = requests.get('%s/followedgames' % my_url)
followed = re.findall(r'data-appid="([0-9]+)"', r.text)

# Get owned games
r = requests.get('%s/games/?tab=all' % my_url)
owned = re.findall(r'"appid":([0-9]+),', r.text)

# To store app data in
discounts_json = 'wishlist.json'
apps = []
old_apps = []
if path.isfile(discounts_json):
    old_apps = [json.loads(line.strip()) for line in open(discounts_json, 'r')]

email_body = ''

watchlist = list(set(wishlist + followed))

# Iterate each appid in the watchlist
for item in watchlist:

    # Skip games we already own
    if item in owned:
        continue

    appid = str(item)

    old = None
    for app in old_apps:
        if appid in app:
            old = app
            break

    url = '{url}/api/appdetails?appids={appids}&cc={region}'\
          .format(url=store_url, appids=appid, region=config['region'])
    print url

    r = requests.get(url)
    j = r.json()

    if not j or appid not in j or 'data' not in j[appid] or\
       'price_overview' not in j[appid]['data'] or\
       'discount_percent' not in j[appid]['data']['price_overview']:
        continue

    if old is not None:
        name = j[appid]['data']['name'].encode('utf-8', 'ignore')

        discount = j[appid]['data']['price_overview']['discount_percent']
        old_discount = old[appid]['data']['price_overview']['discount_percent']

        price = j[appid]['data']['price_overview']['final']
        old_price = old[appid]['data']['price_overview']['final']

        price_fmt = config['currency'] + str(float(price) / 100)
        old_price_fmt = config['currency'] + str(float(old_price) / 100)

        if discount > old_discount or price < old_price:
            email_body += '<a href="%s">%s</a>' % (app_url % appid, name)
            if discount != 0:
                email_body += ' -' + str(discount) + '%'
            email_body += ' ' + price_fmt
            email_body += ' (from'
            if old_discount != 0:
                email_body += ' -' + str(old_discount) + '%'
            email_body += ' ' + old_price_fmt + ')<br />\n'

    apps.append(j)

if config['mail_to'] and email_body:
    email_alert('Steam price updates', None, email_body)
    print email_body

f = open(discounts_json, 'w')
for app in apps:
    f.write(json.dumps(app) + '\n')
f.close()
