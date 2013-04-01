import lxml.html, feedparser, peewee, json, datetime, bottle
import xml.etree.ElementTree as ET
from bottle import route, run, view, install, hook, request, response
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
	title = CharField()
	updated = DateTimeField(default = datetime.datetime(1900, 1, 1))
	url = CharField(unique = True)
	
	def update_feed(self):
			feed = feedparser.parse(self.url)
			feed_updated = datetime.datetime.fromtimestamp(mktime(feed.updated_parsed))
			if (feed_updated> self.updated):
				for item in feed.entries:
					try: Item.get(Item.url == item.link)
					except Item.DoesNotExist:
						Item.create(title = item.title, description = item.description, url = item.link, channel = self)
				
				self.updated = feed_updated
				self.save()
	
class Item(BaseModel):
	title = CharField()
	description = CharField()
	url = CharField(unique = True)
	read = BooleanField(default = False)
	starred = BooleanField(default = False)
	channel = peewee.ForeignKeyField(Channel)

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
	item = Item.get(Item.id == id)
	valid_keys = ['read', 'starred']
	for key in set(valid_keys).intersection(set(request.json.keys())):
		setattr(item, key, request.json[key])
		
	item.save()	
	return response.status

@route('/channels/<url:re:.+>/items')
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
	pass

@route("/")
@route("/<url:re:.+>")
@view('index')
def index(url = ''):	
	index = dict(channel_items(url),**channels())
	index['url'] = url
	return index	
	

run(host='localhost', port=3000, reloader = True, debug = True)
