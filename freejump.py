from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson as json

# Free jump the shorten url to the original long url
# Many shortend url services like bit.ly, j.mp are bloody damn
# blocked in some countries.

# Use like: http://yourapp.appspot.com/freejump?url=http://biy.ly/fuckGFW

class FreejumpPage(webapp.RequestHandler):
    def get_(self):
        short_url = self.request.get('url')
        result = urlfetch.fetch(url=short_url,
                                method='HEAD',
                                follow_redirects=False)
        if result.status_code in (301,302):
            self.redirect(result.headers['Location'])
            # Not setting follow_redirects to False, we can use the final_url
            # self.redirect(result.final_url)
        else:
            self.redirect(short_url)

    def get(self):
        req = "http://api.longurl.org/v2/expand?format=json"
        url = self.request.get('url')
        title = self.request.get('title')
        nojump = self.request.get('nojump')  # redirect to the long url by default 
        if not url: return
        if title:
            req += "&title=1"
        req += "&url=%s" % url
        res = json.loads(urlfetch.fetch(req).content)
        if nojump:
            self.response.out.write("%s:;;:%s" % (res["long-url"],
                                                  "title" in res and res["title"] or ""))
        else:
            self.redirect(res["long-url"])
# End.
