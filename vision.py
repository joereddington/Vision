#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, urllib.error
import json
from urllib.request import urlopen, Request
import os

def get_json_from_url(url):
    config = json.loads(open(os.path.dirname(os.path.abspath(__file__))+'/config.json').read())
    token = config['token']
    request = Request(url)
    request.add_header('Authorization', 'token %s' % token)
    request.add_header('Accept', "application/vnd.github.inertia-preview+json" )
    response = urlopen(request)
    #return json.loads(response.read())
    #Below needed for pre 3.6 python
    return json.loads(response.read().decode('utf-8'))

def process_cards(pri,url, tag=""):
   cards= get_json_from_url(url)
   for card in cards: 
       payload=""
       if card['note']:
            payload="map project:"+ card['note']
       else:
            payload="Work on: "+ card['content_url']
       print("({}) {} {}".format(pri,payload,tag))
   

def process_project_board(url,tag=""):
   board= get_json_from_url(url)
   columns_url= board["columns_url"]
   columns= get_json_from_url(columns_url)
   priorities=['*', 'A', 'B', 'C', 'D','E']
   for x in columns:
      process_cards(priorities.pop(0),x['cards_url'],tag)

if __name__ == "__main__":
   process_project_board("https://api.github.com/projects/1613733","+EQT")
   process_project_board("https://api.github.com/projects/3314213","+PersonalProjects")



