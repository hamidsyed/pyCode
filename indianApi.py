#sk-live-18ZDDMFoqfOd6Kmds75tZg1kqAcsMFJHlKS5YUIo

import http.client

conn = http.client.HTTPSConnection("weather.indianapi.in")

headers = { 'X-Api-Key': "sk-live-18ZDDMFoqfOd6Kmds75tZg1kqAcsMFJHlKS5YUIo" }

#conn.request("GET", "/india/cities", headers=headers)

#res = conn.getresponse()
#data = res.read()

#print(data.decode("utf-8"))
import http.client


conn = http.client.HTTPSConnection("weather.indianapi.in")

headers = { 'X-Api-Key': "sk-live-18ZDDMFoqfOd6Kmds75tZg1kqAcsMFJHlKS5YUIo" }

conn.request("GET", "/india/weather?city=Chennai-meenambakkam", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
"""

conn = http.client.HTTPSConnection("weather.indianapi.in")

headers = { 'X-Api-Key': "sk-live-18ZDDMFoqfOd6Kmds75tZg1kqAcsMFJHlKS5YUIo" }

conn.request("GET", "/india/cities", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
"""

"""
conn = http.client.HTTPSConnection("weather.indianapi.in")

headers = { 'X-Api-Key': "sk-live-18ZDDMFoqfOd6Kmds75tZg1kqAcsMFJHlKS5YUIo" }

conn.request("GET", "/india/weather_by_id?city_id=99922", headers=headers)
#conn.request("GET", "/india/weather?city=New delhi-lodi road, headers=headers)
#conn.request("GET", "/india/cities", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
"""

