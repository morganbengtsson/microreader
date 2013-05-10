import feedparser, json
from bottle import route, run, view, template, install, redirect, hook, request, response, abort, static_file, JSONPlugin

import mimerender

from models import *

class CustomJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
		if isinstance(obj, Model):			
			return obj.__dict__['_data']
		return json.JSONEncoder.default(self, obj)

install(JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))

mimerender = mimerender.BottleMimeRender()
render_json = lambda **args: json.dumps(args, cls=CustomJsonEncoder)

@hook('before_request')
def db_connect():
	db.connect()	

@hook('after_request')
def db_disconnect():
	db.close()

@route("/")
@route("/:id")
@mimerender(default = 'html', json = render_json, html = lambda **args: template('index', args) )
def index(id = ''):	
	index = dict((channel_items(id) if id else items()),**channels())
	return index

@route('/items')
def items():
	since_id  = request.query.since_id
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
			

	
@route('/starred')
@view('index')
def starred():
	starred = dict({"items" : [i for i in Item.select().where(Item.starred == True)]},**channels())
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
