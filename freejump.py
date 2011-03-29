from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson as json
from urllib2 import urlopen
from urllib import quote as urlquote
import re
import logging

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

        try:
            f = urlopen(url)
        except Exception, reason:
            logging.error(str(reason))
            return str(reason)

        html_head = ''
        while True:
            res = f.read(1024)
            html_head += res
            if not res or html_head.find('</head>') != -1: break

        title_raw = re.findall('<title>.*</title>', html_head, flags=re.DOTALL)

        title = title_raw[0][7:-8].strip()  # strip 'title' tag & '\n', '\t'...
        if not title:
            logging.error('NO_TITLE: %s' % url)
            return 'No title found in your web page...'

        for enc in ("utf-8", "gbk", "big5"):
            try:
                t = title.decode(enc)
            except:
                continue
            break
        return t

    def get(self):
        # just quote '\xd1cc' like strings
        urlquote_reserved = ";/?:@&=+$,#%"

        url = self.request.get('url')
        title = self.request.get('title')
        nojump = self.request.get('nojump')  # redirect to the long url by default

        # most of the input urls are 'utf8', our page enc & twitter's are 'utf8'
        url = urlquote(url.encode('utf8'), safe=urlquote_reserved)
        if not url:
            self.response.out.write("Please give us the url...")
            return
        try:
            actual_url = urlquote(self.get_actual_url(url), safe=urlquote_reserved)
            actual_title = ""
            if title:
                actual_title = self.get_title(actual_url)
        except Exception, e:
            self.error(400)
            self.response.out.write(e)
            return
        if nojump:
            self.response.out.write("%s:;;:%s" % (actual_url,
                                                  actual_title and actual_title or ""))
        else:
            self.redirect(actual_url)
# End.
