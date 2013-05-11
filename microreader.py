import feedparser, json
from bottle import route, run, view, template, install, redirect, hook, request, response, abort, static_file, JSONPlugin

from models import *

class CustomJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
		if isinstance(obj, Model):			
			return obj.__dict__['_data']
		return json.JSONEncoder.default(self, obj)

install(JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))

@hook('before_request')
def connect():
	db.connect()	

@hook('after_request')
def disconnect():
	db.close()

@route('/')
def index():
	redirect('/items')
	
@route('/items', method = 'GET')
def items():
	valid_params = {'1' : True, '0' : False}
	starred = valid_params.get(request.query.getone('starred'))
	
	since_id  = request.query.since_id
	max_id = request.query.max_id
	count = int(request.query.count) if request.query.count else None
	page = int(request.query.page) if request.query.page else None
	
	print (starred)

	query = Item.select()
	if starred: query = query.where(Item.starred == starred)
	if since_id: query = query.where(Item.id >= since_id)
	if max_id: query = query.where(Item.id <= max_id)
	if page: query = query.paginate(page, count)	
	
	return {'items' : [i for i in query.order_by(Item.updated.desc()).limit(count)]}

@route('/items/:id', method = 'GET')
def item(id):
	try: 
		item = Item.get(Item.id == id)
	except Item.DoesNotExist:
		abort(404, 'Item does not exist')
	return {'item' : item}

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
	
@route('/starred')
@view('index')
def starred():
	starred = dict({ 'items' : [i for i in Item.select().where(Item.starred == True)]}, **channels())
	return starred

@route("/channels", method = 'GET')
@route("/channels/:id", method = 'GET')
def root(id = ''):
	return dict({'channels' : Channel.select()}, **{'items' : Item.select().where(Item.channel == id) if id else Item.select()})

#@route('/channels', method = 'GET')
#@mimerender(default = 'html', json = render_json)
#	return {'channels' : Channel.select()}

@route('/channels/:id/delete', method = 'GET')
def delete_channel_confirm(id):
	try: 
		channel = Channel.get(Channel.id == id)
	except Channel.DoesNotExist:
		abort(404)
	return template('Delete channel {{channel.title}}?<form action="/channels/{{channel.id}}/delete" method="post"><input type ="submit" name="Ok"></form>', channel = channel)

@route('/channels/:id', method = 'DELETE')
@route('/channels/:id/delete', method = 'POST')
def delete_channel(id):
	try:
		c = Channel.get(Channel.id == id)
		Item.delete().where(Item.channel == c).execute()	
		Channel.delete().where(Channel.id == id).execute()			
	except Channel.DoesNotExist:
		abort(404, 'Channel does not exist')
	redirect('/')	
	
@route('/channels/add', method = 'GET')
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
	redirect('/' + str(channel.id))

@route('/channels/:id/items')
def channel_items(id = ''):
	try: 
		c = Channel.get(Channel.id == id)		
	except Channel.DoesNotExist:
		abort(404, 'Channel does not exist')
	
	return {'items' : [i for i in Item.select().order_by(Item.updated.desc()).where(Item.channel == c)]}

@route('/channels/:id/update', method='GET')
def update_channel(id):
	try: 
		c = Channel.get(Channel.id == id)
		c.update_feed()		
	except Channel.DoesNotExist:
		abort(404)
	return response.status
		

	
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
