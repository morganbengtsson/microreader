import feedparser, json, bottle
import lxml.html
import xml.etree.ElementTree as ET
from datetime import datetime
from bottle import route, run, view, install, redirect, hook, request, response, abort, static_file
from peewee import *
from time import mktime

class CustomJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
		if isinstance(obj, Model):			
			return obj.__dict__['_data']
		return json.JSONEncoder.default(self, obj)

install(bottle.JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))

db = SqliteDatabase('database.db')

class BaseModel(Model):
	class Meta:
		database = db

class Channel(BaseModel):
	title = TextField()
	updated = DateTimeField(default = datetime(1900, 1, 1))
	url = TextField(unique = True)
	icon = TextField(default = '/static/feed.png')
			
	def unread_count(self):
		return Item.select().where(Item.channel == self & Item.read == False).count()
	
	def new_count(self):
		feed = feedparser.parse(self.url)
		count = 0
		try:
			item = Item.get(Item.channel == self)
			for e in feed.entries:
				if e.link == item.url : break
				count += 1
		except Item.DoesNotExist:
			count = len(feed.entries)	
		return count
	
	def update_feed(self):
			feed = feedparser.parse(self.url)
			feed_updated = datetime(3000, 1, 1)
			if 'updated_parsed' in feed : 
				feed_updated = datetime.fromtimestamp(mktime(feed.updated_parsed))
			if (feed_updated > self.updated):
				for entry in feed.entries:
					updated = datetime.fromtimestamp(mktime(entry.updated_parsed))
					description = entry.content[0].value if hasattr(entry, 'content') else entry.description
					description = lxml.html.fromstring(description).text_content()
					
					parameters = dict(updated = updated, title = entry.title, description = description, author = entry.author, url = entry.link, channel = self)
					if not Item.select().where(Item.url == entry.link).exists():						
						Item.create(**parameters)
					else:
						Item.update(**parameters).where(Item.url == entry.link).execute()
						
				
			self.updated = feed_updated
			self.save()
	@classmethod
	def create_from_url(cls, url):
		feed = feedparser.parse(url)
		if not 'title' in feed.feed : raise cls.FeedDoesNotExist
		cls.create(url = url, title = feed.feed.title)
	class FeedDoesNotExist(Exception) : pass
	
class Item(BaseModel):
	title = TextField()
	description = TextField()
	author = TextField()
	url = TextField(unique = True)
	read = BooleanField(default = False)
	starred = BooleanField(default = False)
	channel = ForeignKeyField(Channel, cascade = True)
	updated = DateTimeField()
	
Channel.create_table(fail_silently = True)
if not Channel.select().where(Channel.url == "http://rss.slashdot.org/Slashdot/slashdot").exists():
	Channel.create_from_url("http://rss.slashdot.org/Slashdot/slashdot")
Item.create_table(fail_silently = True)

@hook('before_request')
def db_connect():
	db.connect()	

@hook('after_request')
def db_disconnect():
	db.close()

@route('/items')
def items():
	since_id = request.query.since_id
	max_id = request.query.max_id
	count = int(request.query.count) if request.query.count else None
	page = int(request.query.page) if request.query.page else None

	query = Item.select()
	if since_id: query = query.where(Item.id >= since_id)
	if max_id: query = query.where(Item.id <= max_id)
	if page: query = query.paginate(page, count)	
	
	return {'items' : [i for i in query.order_by(Item.updated.desc()).limit(count)]}

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

@route('/channels/:id', method = 'DELETE')
def delete_channel(id):
	try:
		c = Channel.get(Channel.id == id)
		Item.delete().where(Item.channel == c).execute()	
		Channel.delete().where(Channel.url == url).execute()			
	except Channel.DoesNotExist:
		abort(404)	

@route('/channels/:id/items')
def channel_items(id = ''):
	try: 
		c = Channel.get(Channel.id == id)
		c.update_feed()
	except Channel.DoesNotExist:
		c = Channel.create_from_url(url)
	
	return {'items' : [i for i in Item.select().order_by(Item.updated.desc()).where(Item.channel == c)]}

@route('/channels')
def channels():
	return {'channels' : [c for c in Channel.select()]}
	
@route('/channels', method = 'POST')
def post_channel():			
	try:		
		Channel.create_from_url(request.forms.get('url'))
	except:
		abort(404, "Feed does not exist")
	redirect('/' + request.forms.get('url'))
			
@route("/")
@route("/:id")
@view('index')
def index(id = ''):	
	index = dict((channel_items(id) if id else items()),**channels())
	index['url'] = id
	return index	
	
@route('/starred')
@view('index')
def starred():
	starred = dict({"items" : [i for i in Item.select().where(Item.starred == True)]},**channels())
	starred['url'] = 'starred'
	return starred
	
@route('/static/<filename>')
def server_static(filename):
	return static_file(filename, root='static/')

@route('/favicon.ico')
def get_favicon():
    return server_static('favicon.ico')

try:
	from mod_wsgi import version
except:
	run(host='0.0.0.0', port=3000, reloader = True, debug = True)
