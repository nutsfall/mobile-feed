from google.appengine.ext import db

class FriendFeedUsers(db.Model):
  googleuser = db.UserProperty()
  nickname = db.StringProperty()
  remotekey = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
