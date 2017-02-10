import urllib, json
from urllib2 import urlopen, Request

def get_issues(target):
    url = 'https://api.github.com/repos/%s/issues' % target
    config = json.loads(open('config.json').read())
    token = config["token"]
    request=Request(url)
    request.add_header('Authorization', 'token %s' % token)
    response = urlopen(request)
    return json.loads(response.read())


target = 'joereddington/Vision'
data = get_issues(target)
data.extend(get_issues('equalitytime/whitewaterwriters'))
data.extend(get_issues('equalitytime/home'))

data = sorted(data, key=lambda k: k['title'])
for i in data:
    print i["title"]

for i in data:
    print i["comments_url"]
