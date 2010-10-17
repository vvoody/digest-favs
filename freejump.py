from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson as json
from urllib2 import urlopen
import re

# Free jump the shorten url to the original long url
# Many shortend url services like bit.ly, j.mp are bloody damn
# blocked in some countries.

# Use like: http://yourapp.appspot.com/freejump?url=http://biy.ly/fuckGFW

class FreejumpPage(webapp.RequestHandler):
    def get_actual_url(self, short_url):
        """Get the Location HTTP header of the shortened url."""

        res = urlfetch.fetch(url=short_url, method='HEAD', follow_redirects=False)
        if res.status_code in (301,302):
            return res.headers['Location']
            # Not setting follow_redirects to False, we can use the final_url
            # self.redirect(res.final_url)
        else:
            return short_url  # actuall not shortened, not fool me...

    def get_title(self, url):
        """Get the title of the url."""

        f = urlopen(url)
        res = f.read(500)
        title_raw = re.findall('<title>.*</title>', res)
        if not title_raw: return "No title found of the page..."
        title = title_raw[0][7:-8]  # strip 'title' tag
        for enc in ("utf-8", "gbk", "big5"):
            try:
                t = title.decode(enc)
            except:
                continue
            break
        return t

    def get(self):
        url = self.request.get('url')
        title = self.request.get('title')
        nojump = self.request.get('nojump')  # redirect to the long url by default 
        if not url:
            self.response.out.write("Please give us the url...")
            return
        actual_url = self.get_actual_url(url)
        actual_title = ""
        if title:
            actual_title = self.get_title(actual_url)
        if nojump:
            self.response.out.write("%s:;;:%s" % (actual_url,
                                                  actual_title and actual_title or ""))
        else:
            self.redirect(res["long-url"])
# End.
