import lxml.html, feedparser, peewee, json, datetime, bottle
import xml.etree.ElementTree as ET
from bottle import route, run, view, install
from peewee import *

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
	updated = DateTimeField(default = datetime.datetime.now())
	url = CharField(unique = True)
	
class Item(BaseModel):
	title = CharField()
	description = CharField()
	url = CharField(unique = True)
	read = BooleanField(default = False)
	starred = BooleanField(default = False)
	channel = peewee.ForeignKeyField(Channel)

db.connect()
Channel.create_table(fail_silently = True)
Item.create_table(fail_silently = True)
db.close()

@route('/api/<url:re:.+>')
def items(url = ''):
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
			#i = Item.create(title = item.title, description = item.description, url = item.link)
	return items

@route('/api')
def channels():
	tree = ET.parse('subscriptions.xml')
	#for channel in tree.getroot().findall('./body/outline'):		
		#Channel.create(title = channel.get('title'), url = channel.get('xmlUrl'))
			
	return {'channels' : [c for c in Channel.select().dicts()]}
	
@route("/home")
@route("/home/<url:re:.+>")
@view('index')
def index(url = ''):	
	index = dict(items(url),**channels())
	return index	
	

run(host='localhost', port=3000, reloader = True, debug = True)
