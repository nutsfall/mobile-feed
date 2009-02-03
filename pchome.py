#!-*- coding:utf-8 -*-

#pc画面のhome

import os
import wsgiref.handlers
import cgi
import logging
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
#import friendfeed
# failed to import json
import base64
import urllib

#import my lib
from Model import FriendFeedUsers

class MainPage(webapp.RequestHandler):
   def get(self):

      user = users.get_current_user()
      if user:
          view = 'logined.html'
          template_values = {
                  'logoutUri' : users.create_logout_url(self.request.uri),
                  'username' : user.nickname(),
          }
      else:
          view = 'nologin.html'
          template_values = {
                  'loginUri' : users.create_login_url(self.request.uri),
          }
      
      path = os.path.join(os.path.dirname(__file__), 'templates', 'pchome',  view)
      self.response.out.write(template.render(path, template_values))

### settings page
class Settings(webapp.RequestHandler):
   def get(self):
      # auth
      user = users.get_current_user()
      if user:
          ffusers = FriendFeedUsers.gql("WHERE googleuser = :1", users.get_current_user() )

          nickname = ""
          remotekey = ""
          for ffuser in ffusers:
            logging.info("ffuser %s" % ffuser.googleuser );
            nickname = ffuser.nickname
            remotekey = ffuser.remotekey

          template_values = {
                  'logoutUri' : users.create_logout_url(self.request.uri),
                  'username' : user.nickname(),
                  'nickname' : nickname,
                  'remotekey' : remotekey
          }
          path = os.path.join(os.path.dirname(__file__), 'templates', 'pchome', 'settings.html')
          self.response.out.write(template.render(path, template_values))
      else:
          self.redirect("/")

   def post(self):
      # auth
      user = users.get_current_user()
      if user:
          nickname = cgi.escape(self.request.get('ff_nickname'))
          remotekey = cgi.escape(self.request.get('ff_remotekey'))
          
          #validate to friendfeed
          server = 'friendfeed.com'
          protcol = 'http'
          uri = '/api/feed/home'
          uri_args = {"format" : "xml"}
          args = urllib.urlencode(uri_args)
          url = "%s://%s%s?%s" % (protcol, server, uri, args)
          token_string = "%s:%s" % (nickname, remotekey)
          token = base64.b64encode( token_string )
          
          headers = {'Authorization' : "Basic %s" % token }
          result = urlfetch.fetch( url, headers=headers )
	  
          logging.info("status_code %s " % result.status_code )

          if result.status_code == 200:
              #data store put validate data
              ffuser = FriendFeedUsers(key_name = users.get_current_user().nickname() )
              ffuser.googleuser = users.get_current_user()
              ffuser.nickname = nickname
              ffuser.remotekey = remotekey
              ffuser.put()

              message = 'thanks. save your information.'
          else:
              message = 'sorry, check your remotekey again.'

          template_values = {
                  'logoutUri' : users.create_logout_url(self.request.uri),
                  'username' : user.nickname(),
                  'result' : message,
                  'nickname' : nickname,
                  'remotekey' : remotekey
          }
          path = os.path.join(os.path.dirname(__file__), 'templates', 'pchome', 'settings.html')
          self.response.out.write(template.render(path, template_values))
      else:
          self.redirect("/")
          

def main():
    application = webapp.WSGIApplication(
                                       [('/', MainPage),
                                        ('/settings', Settings)],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
