#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import json
from urllib2 import urlopen, Request
import re
import os

MY_REPO_ROOT="https://api.github.com/users/joereddington"
EQT_REPO_ROOT="https://api.github.com/users/equalitytime"

def get_json_from_url(url):
    config = json.loads(open('/home/joereddington/flow.joereddington.com/vision/config.json').read())
    token = config['token']
    request = Request(url)
    request.add_header('Authorization', 'token %s' % token)
    response = urlopen(request)
    return json.loads(response.read())


def download_comment_to_file(title, url):
    data = get_json_from_url(url)
    with open(os.path.dirname(os.path.abspath(__file__))+'/issues/' + slugify(unicode(title)) + '.md', 'wb') as \
        target_file:
        target_file.write('title: ' + title + '\n')
        for comment in data:
            target_file.write(comment['body'].encode('utf-8'))
            target_file.write('\n')  # Otherwise comments run together


# via http://stackoverflow.com/a/295466/170243 and Django
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """

    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii',
            'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value



repos = []
#repos = get_json_from_url(MY_REPO_ROOT+'/repos')
#repos.extend(get_json_from_url(EQT_REPO_ROOT+'/repos'))
repos.extend(get_json_from_url("https://api.github.com/user/repos"))
issues = []
for repo in repos:
    if repo['has_issues']:
        issues.extend(get_json_from_url(repo['url'] + '/issues?state=all&filter=all'))

issues.extend(get_json_from_url('https://api.github.com/repos/equalitytime/whitewaterwriters' + '/issues?state=all&filter=all'))
issues = sorted(issues, key=lambda k: k['title'])
deadlines=[]
for issue in issues:
    if '2017' in issue['title']:
        deadline={}
        #then it probably has a real deadline.
        print issue['title']
        deadline['date']=issue['title'][:10]
        deadline['action']=issue['title'][11:]
        deadline['state']=issue['state']
        deadline['url']=issue['url']
        deadlines.append(deadline.copy())
    download_comment_to_file(issue['title'], issue['comments_url'])


with open('deadlines.json',"w") as out_file:
    json.dump(deadlines, out_file)


