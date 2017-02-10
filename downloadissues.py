import urllib, json
from urllib2 import urlopen, Request
import re

def get_json_from_url(url):
    config = json.loads(open('config.json').read())
    token = config["token"]
    request=Request(url)
    request.add_header('Authorization', 'token %s' % token)
    response = urlopen(request)
    return json.loads(response.read())

def get_issues(target):
    url = 'https://api.github.com/repos/%s/issues' % target
    return get_json_from_url(url)

def download_comment_to_file(title,url):
    data =get_json_from_url(url)
    with open("issues/"+slugify(unicode(title))+'.md', 'wb') as target_file:
        target_file.write("title: "+title+"\n")
        for comment in data:
             target_file.write(comment['body'])

#via http://stackoverflow.com/a/295466/170243 and Django
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value


target = 'joereddington/Vision'
data = get_issues(target)
data.extend(get_issues('equalitytime/whitewaterwriters'))
data.extend(get_issues('equalitytime/home'))

data = sorted(data, key=lambda k: k['title'])
for issue in data:
    print issue["title"]
    download_comment_to_file(issue["title"],issue["comments_url"])

#download_comment_to_file("test","https://api.github.com/repos/joereddington/Vision/issues/1/comments")
