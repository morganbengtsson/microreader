import feedparser, sqlite3, bottle
import lxml.html
from bottle import route, run, view, SimpleTemplate

@route('/')
def index():
	return "test"

@route('/items')
def items():
	conn = sqlite3.connect('database.db')
	c = conn.cursor()

@route('/rss')
@view('channels')
@route('/api/rss')
def channels():
	feed = feedparser.parse('http://rss.slashdot.org/Slashdot/slashdot')
	
	name_map = {'title' : 'title'}
	items = {'items' : []}
	for item in feed.entries:
		items['items'].append({'title': item.title, 
							   'description' : lxml.html.fromstring(item.description).text_content(),
							   'link' : item.link})
	
	return items
	
		

run(host='localhost', port=3000, reloader = True, debug = True)
