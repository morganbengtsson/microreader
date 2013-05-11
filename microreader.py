import feedparser, json
from bottle import Request, route, run, view, template, install, redirect, hook, request, response, abort, static_file, JSONPlugin

from models import *

class CustomJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
		if isinstance(obj, Model):			
			return obj.__dict__['_data']
		return json.JSONEncoder.default(self, obj)

install(JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))

def accept_json(self):
	return True if (self.get_header('Accept') == 'application/json') else False

Request.accept_json = accept_json

def is_active(url):
	fullpath = request.path + ('?' + request.query_string if request.query_string else '')
	return 'active' if fullpath == url else ''

@hook('before_request')
def connect():
	db.connect()	

@hook('after_request')
def disconnect():
	db.close()

@route('/')
def index():
	redirect('/items')

@route('/channels/<id:int>/items', method = 'GET')	
@route('/items', method = 'GET')
def items(id = None):
	valid_params = {'1' : True, '0' : False}
	starred = valid_params.get(request.query.getone('starred'))
	read = valid_params.get(request.query.getone('read'))
	
	channel = request.query.channel or id
	since_id  = request.query.since_id
	max_id = request.query.max_id
	count = int(request.query.count) if request.query.count else None
	page = int(request.query.page) if request.query.page else None

	query = Item.select()
	if channel: query = query.where(Item.channel == channel)
	if starred: query = query.where(Item.starred == starred)
	if read: query = query.where(Item.read == read)
	if since_id: query = query.where(Item.id >= since_id)
	if max_id: query = query.where(Item.id <= max_id)
	if page: query = query.paginate(page, count)	
	
	items = list(query.order_by(Item.updated.desc()).limit(count))
	if (request.accept_json()):
		return { 'items' : items }
	else:
		return template('index', items = items, channels = Channel.select(), is_active = is_active)
	
@route('/items/<id:int>', method = 'GET')
def item(id):
	try: 
		item = Item.get(Item.id == id)
	except Item.DoesNotExist:
		abort(404, 'Item does not exist')
	return {'item' : item}

@route('/items/<id:int>', method = 'PATCH')
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
	
@route("/channels", method = 'GET')
def channels():
	return { 'channels' : Channel.select() }

@route("/channels/<id:int>", method = 'GET')
def channel(id):	
	try: 
		channel = Channel.get(Channel.id == id)
	except: 
		abort(404, 'Channel does not exist')
	return { 'channel' : channel }

@route('/channels/<id:int>/delete', method = 'GET')
def delete_channel_confirm(id):
	try: 
		channel = Channel.get(Channel.id == id)
	except Channel.DoesNotExist:
		abort(404)
	tpl = """Delete channel {{channel.title}}? 
	<form action="/channels/{{channel.id}}/delete" method="post">
	<input type ="submit" value="Ok"></form>"""
	return template(tpl, channel = channel)

@route('/channels/<id:int>', method = 'DELETE')
@route('/channels/<id:int>/delete', method = 'POST')
def delete_channel(id):
	try:
		c = Channel.get(Channel.id == id)
		Item.delete().where(Item.channel == c).execute()	
		Channel.delete().where(Channel.id == id).execute()			
	except Channel.DoesNotExist:
		abort(404, 'Channel does not exist')
	redirect('/')	
	
@route('/channels/create', method = 'GET')
def create_channel():
	return """<form action="/channels" method="POST">
		Url: <input type="text" name = "url" class="url"/>
		<input type="submit" value = "Add">"""

@route('/channels', method = 'POST')
def post_channel():
	url = request.forms.get('url')
	try:		
		Channel.create_from_url(url)
	except:
		abort(404, "Feed does not exist")
	channel = Channel.get(Channel.url == url)
	channel.update_feed()
	redirect('/channels/' + str(channel.id) + "/items")

@route('/blaaa', method = 'GET')
def update_channels():
	for c in Channel.select():
		c.update()
	return redirect('/items')

@route('/channels/<id:int>/update', method='GET')
def update_channel(id):
	try: 
		c = Channel.get(Channel.id == id)
		c.update_feed()		
	except Channel.DoesNotExist:
		abort(404)
	return redirect('/channels/' + str(c.id) + 'items')
	
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
