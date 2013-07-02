import feedparser, json, urllib, math
#from urlparse import urlunsplit, urlunparse
from functools import partial
from bottle import Request, route, run, view, template, install, redirect, hook, request, response, abort, static_file, JSONPlugin
from models import *
from mimerender import *


class CustomJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
		if isinstance(obj, Model):			
			return obj.__dict__['_data']
		return json.JSONEncoder.default(self, obj)

install(JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))

def is_active(url):
	params = request.query
	valid_keys = ('starred')
	valid_params = dict((k,v) for k, v in params.items() if k in valid_keys)
	fullpath = urllib.parse.urlunsplit(('', '', request.path, urllib.parse.urlencode(valid_params), ''))
	#fullpath = request.path + ('?' + request.query_string if request.query_string else '')
	return 'active' if fullpath == url else ''

mimerender = BottleMimeRender(global_charset = 'utf8')

render_json = lambda **args: json.dumps(args, cls=CustomJsonEncoder)
render_html = lambda tpl='index', **args: lambda **args: template(tpl, channels = Channel.select(), is_active = is_active, **args)

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
@mimerender(json = render_json, html = render_html('index'))
def items(id = None):
	valid_params = {'1' : True, '0' : False}
	starred = valid_params.get(request.query.getone('starred'))
	read = valid_params.get(request.query.getone('read'))
	
	channel = request.query.channel or id
	since_id  = request.query.since_id
	max_id = request.query.max_id
	count = int(request.query.count) if request.query.count else 25
	page = int(request.query.page) if request.query.page else 1

	query = Item.select()
	if channel: query = query.where(Item.channel == channel)
	if starred: query = query.where(Item.starred == starred)
	if read: query = query.where(Item.read == read)
	if since_id: query = query.where(Item.id >= since_id)
	if max_id: query = query.where(Item.id <= max_id)
	total_count = query.count()
	if page and count: query = query.paginate(page, count)	
	
	out = { 'items' : list(query.order_by(Item.updated.desc()).limit(count))}	
	
	params = request.query
	params['page'] = page + 1
	out['next'] = urllib.parse.urlunsplit(('', '', request.path, urllib.parse.urlencode(params), '')) if page <= math.ceil(total_count / count) else None
	params['page'] = page - 1 if page > 1 else 1
	out['prev'] = urllib.parse.urlunsplit(('', '', request.path, urllib.parse.urlencode(params), '')) if page > 1 else None
	
	return out
		
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

	return template('delete', channel = channel)

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
	return template('create')

@route('/channels', method = 'POST')
def post_channel():
	url = request.forms.get('url')			
	Channel.create_from_url(url)	
	channel = Channel.get(Channel.url == url)
	channel.update_feed()
	redirect('/channels/' + str(channel.id) + "/items")

@route('/channels/<id:int>/edit', method = 'GET')
def edit_channel(id):
	channel = Channel.get(Channel.id == id)
	return template('edit', channel = channel)

@route('/channels/<id:int>/edit', method = 'POST')
def edit_channel_post(id):	
	title = request.forms.get('title')
	url = request.forms.get('url')
	channel = Channel.get(Channel.id == id)
	channel.title = title
	channel.url = url
	channel.save()
	redirect('/channels/' + str(channel.id) + "/items")

@route('/channels/update', method = 'GET')
def update_channels():
	for c in Channel.select():
		c.update_feed()
	return redirect('/items')

@route('/channels/<id:int>/update', method='GET')
def update_channel(id):
	try: 
		c = Channel.get(Channel.id == id)
		c.update_feed()		
	except Channel.DoesNotExist:
		abort(404)
	return redirect('/channels/' + str(c.id) + '/items')
	
@route('/static/<filename>')
def server_static(filename):
	return static_file(filename, root='static/')

@route('/favicon.ico')
def get_favicon():
    return server_static('favicon.ico')

if __name__ == '__main__':
	try:
		from mod_wsgi import version
	except:
		run(host='0.0.0.0', port=3000, reloader = True, debug = True)
