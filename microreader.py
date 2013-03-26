import feedparser, bottle
import xml.etree.ElementTree as ET
from bottle import route, run, view, SimpleTemplate

@route('/api/<url:re:.+>')
def items(url):
	feed = feedparser.parse(url)	
	items = {'items' : []}
	for item in feed.entries:
		items['items'].append({'title': item.title, 
							   'description' : item.description,
							   'link' : item.link})
	return items

@route('/api')
def channels():
	tree = ET.parse('subscriptions.xml')
	channels = {'channels' : []}
	print (tree.getroot().findall('./body/outline'))
		
	for channel in tree.getroot().findall('./body/outline'):
		channels['channels'].append({'title' : channel.get('title'), 'url' : channel.get('xmlUrl')})
	
	return channels
@route("/")
@route("/<url:re:.+>")
@view('index')
def index(url = ''):
	index = dict(items(url),**channels())
	return index
	

run(host='localhost', port=3000, reloader = True, debug = True)
