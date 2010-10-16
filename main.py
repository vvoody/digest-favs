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

from simplecookies import Cookies

class MainHandler(webapp.RequestHandler):
    def get_(self):
        cookies = Cookies(self, max_age=180)
        if 'user' in cookies:
            self.response.out.write(cookies['user'])
        else:
            cookies['user'] = 'vvoody'

    def render(self, template_values):
        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))

    def get(self):
        cookies = Cookies(self, max_age=2678400)  # one month expiration
        template_values = {}
        id_ = self.request.get("id")
        instapaper_cookie = "instapaper" in cookies and cookies["instapaper"] or ""
        instapaper_get = self.request.get("instapaper")

        if instapaper_cookie == "" and id_ == "":
            flashes = "First here? 'Howto' page will tell you howto fill up the fields below."
        elif id_ == "":
            flashes = "Please tell us your twitter id."
        elif instapaper_cookie == "" and instapaper_get == "":
            flashes = "Please tell us the link location of your Instapaper's 'Read Later'."
        else:
            if "instapaper" not in cookies:
                cookies["instapaper"] = instapaper_get
            template_values["instapaper"] = instapaper_cookie
            page = self.request.get("p")
            if page == "": page = "1"
            proxy = 'http://ydoovv.appspot.com/'
            url = '%s/favorites/%s.json?page=%s' % (proxy, id_, page)
            res = urlfetch.fetch(url)
            favs = json.loads(res.content)
            template_values = {"tweets": [], "id": id_, "page": int(page) + 1}
            for fav in favs:
                tweet = fav["text"]
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
                for url in urls:
                    tweet = tweet.replace(url, '<a href="%s">%s</a>' % (url, url))
                template_values["tweets"].append({"content":"%s" % tweet, "inlineurl": "%s" % url})
            flashes = "Here is %s's favorites." % id_
            template_values["next"] = "yes"
        template_values["flashes"] = flashes
        self.render(template_values)
        #self.response.out.write(template_values["tweets"])

def main():
    application = webapp.WSGIApplication(
        [
            (r'/', MainHandler),
        ],
        debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
