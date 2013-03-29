import feedparser
import lxml.html
import xml.etree.ElementTree as ET
from bottle import route, run, view

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

run(host='localhost', port=3000, reloader = True, debug = True)
