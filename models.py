from google.appengine.ext import blobstore, ndb


class User(ndb.Model):
    user_id = ndb.StringProperty()
    subscriptions = ndb.StringProperty()


class UserPhoto(ndb.Model):
    user_email = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    restaurant = ndb.StringProperty()
    dish = ndb.StringProperty()
    price = ndb.FloatProperty()
    description = ndb.TextProperty()
    subscriptions = ndb.StringProperty()
    latitude = ndb.StringProperty()
    longitude = ndb.StringProperty()


class Themes(ndb.Model):
    creator_email = ndb.StringProperty()
    subscribers=ndb.StringProperty()
    subscriptions = ndb.StringProperty()
