#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run some bot jobs on GAE."""

import os
import re
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json
from google.appengine.ext.webapp import template

from simplecookies import Cookies
from freejump import FreejumpPage

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
        template_values = {}
        id_ = self.request.get("id")

        if id_ == "":
            flashes = "Please tell us your twitter id."
        else:
            page = self.request.get("p")
            if page == "": page = "1"
            proxy = 'http://ydoovv.appspot.com/'  # a twitter api proxy, or handle yourself
            url = '%s/favorites/%s.json?page=%s' % (proxy, id_, page)
            res = urlfetch.fetch(url)
            if res.content[0] not in ('[', '{'):
                logging.error('BAD_FETCH: %s' % url)
                template_values["flashes"] = 'Bad request!'
                self.render(template_values)
                return
            else:
                favs = json.loads(res.content)
            if isinstance(favs, dict):  # {"request": "oooo", "error": "xxxx"}
                template_values["flashes"] = favs["error"]
                self.render(template_values)
                return
            template_values = {"tweets": [], "id": id_, "page": int(page) + 1}
            for fav in favs:
                tweet = fav["text"]
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
                url = ""
                replaced_urls = {}
                for url in urls:  # not safe, what if have same urls?
                    if url in replaced_urls: continue
                    tweet = tweet.replace(url, '<a href="%s">%s</a>' % (url, url))
                    replaced_urls[url] = True
                template_values["tweets"].append({"content":"%s" % tweet, "inlineurl": "%s" % url})
#                                                  "longurl": "%s" % longurl, "title": "%s" % title})
            flashes = "Here is %s's favorites." % id_
            template_values["next"] = "yes"
        template_values["flashes"] = flashes
        self.render(template_values)

class HowtoPage(webapp.RequestHandler):
    def get(self):
        template_values = {"flashes": "An app that save links from your Twitter's Favorites to Instapaper."}
        template_values["tweets"] = [{"content": "1. Login Instapaper.com"},
                                     {"content": "2. Enter your Twitter id & press 'Get favs!'"},
                                     {"content": "3. click 'Read Later' to save the link to Instapaper"},]
        path = os.path.join(os.path.dirname(__file__), 'templates/howto.html')
        self.response.out.write(template.render(path, template_values))

class AboutPage(webapp.RequestHandler):
    def get(self):
        template_values = {"flashes": "About about."}
        template_values["tweets"] = [{'content': 'Author: vvoody <a href="http://vvoody.org/">vvoody.org</a>'},
                                     {'content': 'Contact: wxj.g.sh_A_T_gmail.com'},
                                     {'content': 'Source: <a href="http://github.com/vvoody/digest-favs">digest-favs@github</a>'},
                                     {'content': 'Contact: A Chinese blog <a href="http://vvoody.org/blog/?p=618">post</a> to know more.'},]
        path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
        self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication(
        [
            (r'/', MainHandler),
            (r'/freejump', FreejumpPage),
            (r'/howto', HowtoPage),
            (r'/about', AboutPage),
        ],
        debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
