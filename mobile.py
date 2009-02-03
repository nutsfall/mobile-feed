#!-*- coding:utf-8 -*-

#携帯画面

import os
import wsgiref.handlers
import cgi
import logging
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from django.utils import simplejson
#import friendfeed
# failed to import json
import base64
import urllib

#import my lib
from Model import FriendFeedUsers

class MainPage(webapp.RequestHandler):
   def get(self):
      #login screen for mobile.
      #after login, feed view.

      user = users.get_current_user()
      if user:
          #fetch feed
          ffusers = FriendFeedUsers.gql("WHERE googleuser = :1", users.get_current_user() )
          
          for ffuser in ffusers:
            logging.info("ffuser %s" % ffuser.googleuser );
            nickname = ffuser.nickname
            remotekey = ffuser.remotekey

          #validate to friendfeed
          server = 'friendfeed.com'
          protcol = 'http'
          uri = '/api/feed/home'
          uri_args = {"format" : "json"}
          args = urllib.urlencode(uri_args)
          url = "%s://%s%s?%s" % (protcol, server, uri, args)
          token_string = "%s:%s" % (nickname, remotekey)
          token = base64.b64encode( token_string )

          headers = {'Authorization' : "Basic %s" % token }
          result = urlfetch.fetch( url, headers=headers )

          logging.info("status_code %s " % result.status_code )
          data = simplejson.loads(result.content)

          view = 'logined.html'
          template_values = {
                  'logoutUri' : users.create_logout_url(self.request.uri),
                  'username' : user.nickname(),
                  'entries' :  data['entries'],
          }
      else:
          view = 'nologin.html'
          template_values = {
                  'loginUri' : users.create_login_url(self.request.uri),
          }
      
      path = os.path.join(os.path.dirname(__file__), 'templates', 'mobile',  view)
      self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication(
                                       [('/m/', MainPage)],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
