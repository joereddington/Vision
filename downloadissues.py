import urllib, json
target = 'joereddington/Vision'
url = 'https://api.github.com/repos/%s/issues' % target
print url
response = urllib.urlopen(url)
data = json.loads(response.read())
print data
for i in data:
    print i["title"]
