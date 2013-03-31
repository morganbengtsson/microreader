import lxml.html, feedparser, peewee, json, datetime, bottle
import xml.etree.ElementTree as ET
from bottle import route, run, view, install, hook
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

@route('/api/items')
def items():
	return {'items' : [i for i in Item.select().dicts()]}

@route('/api/channels/<url:re:.+>/items')
def channel_items(url = ''):
	try: 
		c = Channel.get(Channel.url == url)
		c.update_feed()
	except Item.DoesNotExist:
		c = Null
	
	return {'items' : [i for i in Item.select().where(Item.channel == c).dicts()]}

@route('/api/channels')
def channels():
	return {'channels' : [c for c in Channel.select().dicts()]}
	
@post('/api/channels')
def add_channel():
	

@route("/channels")
@route("/channels/<url:re:.+>")
@view('index')
def index(url = ''):	
	index = dict(channel_items(url),**channels())
	index['url'] = url
	return index	
	

run(host='localhost', port=3000, reloader = True, debug = True)
