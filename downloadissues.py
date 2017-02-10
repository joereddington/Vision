import urllib, json
from urllib2 import urlopen, Request

config = json.loads(open('config.json').read())
token = config["token"]

print token

target = 'joereddington/Vision'
url = 'https://api.github.com/repos/%s/issues' % target
print url
request=Request(url)
request.add_header('Authorization', 'token %s' % token)
response = urlopen(request)
data = json.loads(response.read())
#print data
for i in data:
    print i["title"]
