import feedparser, peewee, json, datetime, bottle
import lxml.html
import xml.etree.ElementTree as ET
from bottle import route, run, view, install, hook, request, response, abort, static_file
from peewee import *
from time import mktime

class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
        return json.JSONEncoder.default(self, obj)

install(bottle.JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))

db = peewee.SqliteDatabase('database.db')

class BaseModel(Model):
	class Meta:
		database = db

class Channel(BaseModel):
	title = TextField()
	updated = DateTimeField(default = datetime.datetime(1900, 1, 1))
	url = TextField(unique = True)
	
	def update_feed(self):
			feed = feedparser.parse(self.url)
			feed_updated = datetime.datetime.fromtimestamp(mktime(feed.updated_parsed))
			#if (feed_updated> self.updated):
			for item in feed.entries:
				if not Item.select().where(Item.url == item.link).exists():
					Item.create(title = item.title, description = lxml.html.fromstring(item.description).text_content(), url = item.link, channel = self)
				else:
					Item.update(title = item.title, description = lxml.html.fromstring(item.description).text_content(), url = item.link, channel = self).where(Item.url == item.link).execute()
					
				
			self.updated = feed_updated
			self.save()
	@classmethod
	def create_from_url(cls, url):
		feed = feedparser.parse(url)
		if not feed.feed.title : raise self.FeedDoesNotExist
		cls.create(url = url, title = feed.feed.title)
	class FeedDoesNotExist(Exception) : pass
	
class Item(BaseModel):
	title = TextField()
	description = TextField()
	url = TextField(unique = True)
	read = BooleanField(default = False)
	starred = BooleanField(default = False)
	channel = peewee.ForeignKeyField(Channel)
	
Channel.create_table(fail_silently = True)
if not Channel.select().where(Channel.url == "http://rss.slashdot.org/Slashdot/slashdot").exists():
	Channel.create(title = "Slashdot", url = "http://rss.slashdot.org/Slashdot/slashdot")
Item.create_table(fail_silently = True)

@hook('before_request')
def db_connect():
	db.connect()
	

@hook('after_request')
def db_disconnect():
	db.close()

@route('/items')
def items():
	return {'items' : [i for i in Item.select().dicts()]}

@route('/items/:id', method = 'PATCH')
def patch_item(id):
	try: 
		item = Item.get(Item.id == id)
	except Item.DoesNotExist:
		abort(404)
		
	valid_keys = ['read', 'starred']
	for key in set(valid_keys).intersection(set(request.json.keys())):
		setattr(item, key, request.json[key])
		
	item.save()	
	return response.status

@route('/channels/<url:re:https?://.+>/items')
def channel_items(url = ''):
	try: 
		c = Channel.get(Channel.url == url)
		c.update_feed()
	except Channel.DoesNotExist:
		c = None
	
	return {'items' : [i for i in Item.select().where(Item.channel == c).dicts()]}

@route('/channels')
def channels():
	return {'channels' : [c for c in Channel.select().dicts()]}
	
@route('/channels', method = 'POST')
def post_channel():			
	try:
		print (request.json)
		Channel.create_from_url(request.json['url'])
	except Channel.FeedDoesNotExist:
		abort(404, "Feed does not exist")
		
@route("/")
@route("/<url:re:https?://.+>")
@view('index')
def index(url = ''):	
	index = dict((channel_items(url) if url else items()),**channels())
	index['url'] = url
	return index	
	

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static/')

run(host='localhost', port=3001, reloader = True, debug = True)
