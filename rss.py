import feedparser, bottle
import xml.etree.ElementTree as ET
from bottle import route, run, view, SimpleTemplate

@route('/')
def index():
	return "test"

@route("/<url:re:.+>")
@route('/api/<url:re:.+>')
@view('feed')
# TODO: strip HTML tags
def feed(url = ''):	
	feed = feedparser.parse(url)	
	items = {'items' : []}
	for item in feed.entries:
		items['items'].append({'title': item.title, 
							   'description' : item.description,
							   'link' : item.link})	
	return items
	
@route('/')
@route('/api')
@view('channels')
def channels():
	tree = ET.parse('subscriptions.xml')
	channels = {'channels' : []}
	print (tree.getroot().findall('./body/outline'))
		
	for channel in tree.getroot().findall('./body/outline'):
		channels['channels'].append({'title' : channel.get('title'), 'url' : channel.get('xmlUrl')})
	
	return channels

run(host='localhost', port=3000, reloader = True, debug = True)
