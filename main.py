#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run some bot jobs on GAE."""

import os
import re

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from google.appengine.ext.webapp import template

class MainHandler(webapp.RequestHandler):
    def get(self):
        id_ = self.request.get("id")
        page = self.request.get("p")
        if page == "": page = "1"
        proxy = 'http://api.twitter.com/1/'
        url = '%s/favorites/%s.json?page=%s' % (proxy, id_, page)
        res = urlfetch.fetch(url)
        favs = json.loads(res.content)
        template_values = {"tweets": [], "id": id_, "page": int(page) + 1, "flashes":{"message": "Here is %s's favorites." % id_}}
        for fav in favs:
            tweet = fav["text"]
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
            for url in urls:
                tweet = tweet.replace(url, '<a href="%s">%s</a>' % (url, url))
            template_values["tweets"].append({"content":"%s" % tweet})
        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication(
        [
            (r'/', MainHandler),
        ],
        debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
