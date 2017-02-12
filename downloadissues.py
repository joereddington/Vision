#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import json
from urllib2 import urlopen, Request
import re

MY_REPO_ROOT="https://api.github.com/users/joereddington"
EQT_REPO_ROOT="https://api.github.com/users/equalitytime"

def get_json_from_url(url):
    config = json.loads(open('config.json').read())
    token = config['token']
    request = Request(url)
    request.add_header('Authorization', 'token %s' % token)
    response = urlopen(request)
    return json.loads(response.read())


def download_comment_to_file(title, url):
    data = get_json_from_url(url)
    with open('issues/' + slugify(unicode(title)) + '.md', 'wb') as \
        target_file:
        target_file.write('title: ' + title + '\n')
        for comment in data:
            target_file.write(comment['body'])
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
repos = get_json_from_url(MY_REPO_ROOT+'/repos')
repos.extend(get_json_from_url(EQT_REPO_ROOT+'/repos'))
issues = []
for repo in repos:
    if repo['has_issues']:
        issues.extend(get_json_from_url(repo['url'] + '/issues?state=all&filter=all'))

#issues.extend(get_json_from_url('https://api.github.com/repos/equalitytime/whitewaterwriters' + '/issues?state=all&filter=all'))
issues = sorted(issues, key=lambda k: k['title'])
for issue in issues:
    print issue['title']
    download_comment_to_file(issue['title'], issue['comments_url'])

