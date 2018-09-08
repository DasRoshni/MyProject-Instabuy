import json
import os

from google.appengine.api import users
from google.appengine.api.images import get_serving_url
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore.blobstore import BlobKey
from google.appengine.api import mail
from google.appengine.api import search


import jinja2
import webapp2
import time

from models import User
from models import UserPhoto
from models import Themes

# bootstrap jinja env needed to use jinja templating engine
# linked to /templates
JINJA_ENV= jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates'))
)

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        filter_tag = self.request.get('filter')
        if filter_tag=="" :
            image_ids = UserPhoto.query().map(lambda x: x.blob_key)
            images = map(lambda x: [str(x), get_serving_url(x)], image_ids)
        else:
            image_ids = UserPhoto.query(UserPhoto.subscriptions==filter_tag).map(lambda x: x.blob_key)
            images = map(lambda x: [str(x), get_serving_url(x)], image_ids)

        if 'Android' in self.request.user_agent:

            if filter_tag=="" :
                images = UserPhoto.query().fetch()
            else:
                images = UserPhoto.query(UserPhoto.subscriptions==filter_tag).fetch()
            for i in range(len(images)):
                images[i] = images[i].to_dict()
                images[i]['src'] = get_serving_url(images[i]['blob_key'])
                images[i]['blob_key'] = str(images[i]['blob_key'])

            self.response.headers['Content-Type'] = 'application/json'
            obj = {
                  'images': images
            }
            self.response.out.write(json.dumps(obj))
        else:
            if user:
                add_theme_btn = \
                    '<a type="button" id="buttontheme" href="/addtheme" style="width:220px; color:black;">' \
                    'Add New Theme</a>'
                upload_photo_button = '<a class="btn" href="/uploadimage">Post Image</a>'
                user_action_url = users.create_logout_url(self.request.uri)
                user_action_url_linktext = 'Logout'
                results = Themes.query().fetch()
            else:
                add_theme_btn = ''
                upload_photo_button = ''
                user_action_url = users.create_login_url(self.request.uri)
                user_action_url_linktext = 'Login'
                results = ""

            subscribe_form = \
                    '<li><form action="/subscribe/{0}" method="POST">' \
                '<button type="submit" class="btn btn-success">Subscribe to: {0}' \
            '</button></form></li>'.format(filter_tag) if filter_tag and user else ''


            # show an alert for the subscribe status
            subscribe_alert = ''
            sub_stat = self.request.get('subscribe')  #TODO: implement correct checks
            if sub_stat == 'success' and user:
                ib_user = User.get_or_insert(user.email())
                if ib_user.subscriptions:
                    last_sub = ib_user.subscriptions.split(',')[-2]
                    subscribe_alert = \
                        '<div class="d-flex justify-content-center"><div id="sub-success-alert" class="snack-alert alert alert-success" role="alert">' \
                        'You are now subscribed to <strong>{}</strong></div></div>'.format(last_sub)


            template_values = {
                'add_theme_btn': add_theme_btn,
                'images': images,
                'subscribe_alert': subscribe_alert,
                'subscribe_form': subscribe_form,
                'upload_photo_button': upload_photo_button,
                'user_action_url': user_action_url,
                'user_action_url_linktext': user_action_url_linktext,
                'results': results,
            }

            template = JINJA_ENV.get_template('index.html')  # grab template file
            # write template contents (which is the html) and render on browser
            self.response.write(template.render(template_values))


# [START image_handler]
class Image(webapp2.RequestHandler):
    def get(self):
        greeting_key = ndb.Key(urlsafe=self.request.get('img_id'))
        greeting = greeting_key.get()
        if greeting.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(greeting.avatar)
        else:
            self.response.out.write('No image')
# [END image_handler]


# [START upload_handler]
class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        if 'Android' in self.request.user_agent:
            rsp = json.load(self.request.body)

            user_email = rsp['email']
            restaurant = rsp['restaurant']
            dish = rsp['dish']
            price = float(rsp['price'])
            describe = rsp['describe']
            subscriptions = rsp('filter')
        else:
            user_email = users.get_current_user().email()
            restaurant = self.request.get("restaurant")
            dish = self.request.get("dish")
            price = float(self.request.get("price"))
            description = self.request.get("description")
            subscriptions = self.request.get("filter")
            print('sub', subscriptions)
            latitude=self.request.get("latitude")
            longitude = self.request.get("longitude")

        pagetondb = UserPhoto(user_email=user_email,
                              blob_key=upload.key(),
                              restaurant=restaurant,
                              dish=dish,
                              price=price,
                              description=description,
                              subscriptions=subscriptions,
                              latitude=latitude,
                              longitude=longitude
                              )
        pagetondb.put()

        time.sleep(0.1)
        self.redirect('/#')
# [END upload_handler]


# [START download_handler]
class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)
# [END download_handler]


#[START Image Upload Page]
class UploadImagePage(webapp2.RequestHandler):
    def get(self):
        filters = Themes.query().fetch()
        upload_url = blobstore.create_upload_url('/upload_photo')
        if 'Android' in self.request.user_agent:
            self.response.headers['Content-Type'] = 'application/json'
            obj = {
                'filters': filters,
                'upload_url': upload_url,
            }
            self.response.out.write(json.dumps(obj))
        else:
            templates={
                    'results': filters,
                    'upload_url': upload_url
                }
            template = JINJA_ENV.get_template('/uploadimage.html')
            self.response.write(template.render(templates))


class SubscribeHandler(webapp2.RequestHandler):
    def post(self, filter_tag):
        if 'Android' in self.request.user_agent:
            rsp = json.load(self.request.body)

            ib_user = User.get_or_insert(rsp['user_email'])
            add_sub = rsp['filter_tag']
        else:
            user = users.get_current_user()
            if user:
                ib_user = User.get_or_insert(user.email())
                add_sub = filter_tag + ','
        if ib_user:
            sub = ib_user.subscriptions
            print('sub', sub)
            if sub is None:
                list = []
                pass
            else:
                list = sub.split(',')
                print('List', list)
                print(filter_tag)
            if filter_tag in list:
                pass
            else:
                ib_user.subscriptions = ib_user.subscriptions + add_sub if \
                 ib_user.subscriptions else add_sub
                ib_user.user_id=users.get_current_user().email()
                ib_user.put()


        self.redirect('/?subscribe=success')


class CreateTheme(webapp2.RequestHandler):
    def post(self):
        if 'Android' in self.request.user_agent:
            rsp = json.load(self.request.body)
            theme_name = rsp['theme_name']
            email = rsp['email']
        else:
            theme_name = self.request.get("theme_name")
            email = users.get_current_user().email()

        themes = Themes.query().filter(Themes.subscriptions==theme_name)
        result=themes.fetch()

        if len(result)==0:
            themetondb = Themes(creator_email=email, subscribers=email, subscriptions=theme_name)
            themetondb.put()
        else:
            print('Theme already in data base')

        time.sleep(0.1)
        self.redirect('/')


class ThemePage(webapp2.RequestHandler):
    def get(self):
        upload_theme = blobstore.create_upload_url('/add_theme')
        if 'Android' in self.request.user_agent:
            self.request.headers['Content-Type'] = 'application/json'
            obj = {
                'upload_theme': upload_theme,
            }
            self.request.out.write(json.dumps(obj))
        else:
            templates = {
                'upload_theme': upload_theme
            }

            template = JINJA_ENV.get_template('/addtheme.html')
            self.response.write(template.render(templates))

#[START Report Display]
class ReportDisplay(webapp2.RequestHandler):
    def get(self, photo_key):
        blob_key = BlobKey(photo_key)
        img_url = get_serving_url(blob_key)
        get_report = UserPhoto.query(UserPhoto.blob_key == blob_key)
        get_report.fetch()
        if 'Android' in self.request.user_agent:
            self.request.header['Content-Type'] = 'application/json'
            obj = {
                'get_report': get_report,
                'img_url': img_url,
            }
            self.request.out.write(json.dumps(obj))
        else:
            templates = {
                'get_report': get_report,
                'img_url': img_url,
            }
            template = JINJA_ENV.get_template('/reportdisplay.html')
            self.response.write(template.render(templates))


#[START subscription email]
def send_approved_mail(sender_address):
    get_usermail=users.get_current_user()
    mail.send_mail(sender=sender_address,
                   to=get_usermail,
                   subject="Subscription Email",
                   body="""Check latest posts!!!""")


class SubscriptionEmails(webapp2.RequestHandler):
    def get(self):
        send_approved_mail('apad.2018.lrr@gmail.com')
        self.response.content_type = 'text/plain'
        self.response.write('Sent an email')


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/upload_photo', PhotoUploadHandler),
    ('/view_photo/([^/]+)?', ViewPhotoHandler),
    ('/uploadimage',UploadImagePage),
    ('/subscribe/([^/]+)?', SubscribeHandler),
    ('/addtheme', ThemePage),
    ('/add_theme',CreateTheme),
    ('/reportdisplay/([^/]+)?', ReportDisplay),
    ('/subscriptionemails',SubscriptionEmails),
], debug=True)
# [END app]
