import feedparser
import lxml.html
import xml.etree.ElementTree as ET
from bottle import route, run, view
import peewee
from peewee import *

class Channel(peewee.Model):
	title = CharField()
	url = CharField()
	
class Item(peewee.Model):
	title = CharField()
	description = CharField()
	url = CharField()
	read = BooleanField(default = False)
	starred = BooleanField(default = False)
	channel = peewee.ForeignKeyField(Channel)
	
def _db():
	db = peewee.SqliteDatabase('database.db')
	db.connect()
	Channel.create_table(fail_silently = True)
	Item.create_table(fail_silently = True)
	return db

@route('/api/<url:re:.+>')
def items(url = ''):
	db = _db()
	items = {'items' : [], 'url' : url}
	
	urls = []
	if url: urls.append(url)
	else:
		for channel in channels()['channels']:
			urls.append(channel['url'])
	
	for url in urls:
		feed = feedparser.parse(url)
		for item in feed.entries:
			items['items'].append({'title': item.title, 
							       'description' : item.description,
							       'link' : item.link})
			i = Item.create(title = item.title, description = item.description, url = item.link)
	
	
	return items

@route('/api')
def channels():
	tree = ET.parse('subscriptions.xml')
	channels = {'channels' : []}
		
	for channel in tree.getroot().findall('./body/outline'):
		channels['channels'].append({'title' : channel.get('title'), 'url' : channel.get('xmlUrl')})
	
	return channels
	
@route("/")
@route("/<url:re:.+>")
@view('index')
def index(url = ''):	
	index = dict(items(url),**channels())
	return index	
	

@route('/bla')
def bla():
	return Channel;

run(host='localhost', port=3000, reloader = True, debug = True)
