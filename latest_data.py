#!/bin/python

##
# SmartMeter Wiener Netze - get latest 1/4h data - Peter Kowalsky, 11.10.2019
##

import sys

##
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
##

from keycloak import KeycloakOpenID
import requests
import pandas
import datetime
import uuid

USERNAME = "demouser"
PASSWORD = "Demouser123"

ZNR = "DEMO00000000000000000000000000001"
DATUM = datetime.date.today() - datetime.timedelta(days=1)

from_date = (DATUM - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
until_date = DATUM.strftime("%Y-%m-%d")

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

print(" ")
print("=================")
print("=== SSO LOGIN ===")
print("=================")
print(" ")


keycloak_openid = KeycloakOpenID(server_url="https://service.wienerstadtwerke.at/auth/",
		client_id="client-smp-public",
		realm_name="wienernetze",
		client_secret_key=uuid.uuid1())

try:
	token = keycloak_openid.token(USERNAME, PASSWORD)
except:
	try:
		print('[' + str(sys.exc_info()[1]).split(":")[0] + '] ' + requests.status_codes._codes[int(str(sys.exc_info()[1]).split(":")[0])][0])
	except:
		print("Network ERROR")
	print(" ")
	sys.exit()

userinfo = keycloak_openid.userinfo(token['access_token'])
print('[200] ' + str(userinfo))

print(" ")
print("===============")
print("=== OPTIONS ===")
print("===============")
print(" ")

URL = "https://service.wienernetze.at/rest/smp/1.0/m/messdaten/export"
URL = URL + "?dateFrom=" + from_date + "T22:00:00.000Z"
URL = URL + "&dateUntil=" + until_date + "T21:59:59.999Z"
URL = URL + "&quarter-hour=true"
URL = URL + "&zaehlpunkte=" + ZNR

headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux ppc64le; rv:66.0) Gecko/20100101 Firefox/66.0',
'Accept': '*/*',
'Access-Control-Request-Method': 'GET',
'Access-Control-Request-Headers': 'authorization,cache-control,content-type,expires,pragma',
'Referer': 'https://www.wienernetze.at/wnapp/smapp/',
'Connection': 'keep-alive'
}

p = requests.options(URL, headers=headers)

print('[' + str(p.status_code) + '] ' + requests.status_codes._codes[p.status_code][0])

if p.status_code != 200:
	keycloak_openid.logout(token['refresh_token'])
	sys.exit()

print(" ")
print("===========")
print("=== GET ===")
print("===========")
print(" ")

URL = "https://service.wienernetze.at/rest/smp/1.0/m/messdaten/zaehlpunkt/" + ZNR + "/verbrauch"
URL = URL + "?dateFrom=" + from_date + "T23:00:00.000Z"
URL = URL + "&quarter-hour=true"
URL = URL + "&period=DAY&accumulate=false&offset=0&dayViewResolution=QUARTER-HOUR"

encoding="ISO-8859-1"

headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux ppc64le; rv:66.0) Gecko/20100101 Firefox/66.0',
'Accept': 'application/vnd.ms-excel; charset=ISO-8859-1',
'Referer': 'https://www.wienernetze.at/wnapp/smapp/',
'Authorization': 'bearer ' + token['access_token'],
'Origin': 'https://www.wienernetze.at',
'Connection': 'keep-alive',
'Cache-control': 'no-cache',
'Pragma': 'no-cache',
'Expires': '-1',
'Content-Type': 'application/vnd.ms-excel; charset=' + encoding.upper()
}

r = requests.get(url = URL, headers = headers)

print('[' + str(p.status_code) + '] ' + requests.status_codes._codes[p.status_code][0])

if p.status_code != 200:
	keycloak_openid.logout(token['refresh_token'])
	sys.exit()

print(" ")
print("============")
print("=== DATA ===")
print("============")
print(" ")

data = json.loads(r.content.decode(encoding.lower()))

sum = 0

for x in data['values']:
    print(x['timestamp'] + " -> " + str(x['value'] * 4) + "W")
    sum = sum + x['value']

print('')

avg = sum / 24

print("Tagesverbrauch -> " + str(sum) + "Wh")
print("Durchschnitt -> " + str(avg) + "W")
print('')


keycloak_openid.logout(token['refresh_token'])
