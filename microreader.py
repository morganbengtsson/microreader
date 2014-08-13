import json
import math

try:
    from urllib.parse import urlencode, urlunsplit
except ImportError:
    from urlparse import urlunsplit
    from urllib import urlencode
from bottle import Response, error, route, run, template, install, redirect, hook, \
    request, response, abort, static_file, JSONPlugin, url
from models import *
import pyfav


@error(500)
@error(404)
@error(403)
@error(510)
def custom_error(error) -> Response:
    if request.get_header('Accept') == 'application/json':
        return Response(json.dumps({'message': error.body}), status=error.status_code)
    else:
        return Response(error.status + ", " + error.body, status=error.status_code)


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
        if isinstance(obj, Model):
            return obj.__dict__['_data']
        return json.JSONEncoder.default(self, obj)


install(JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=CustomJsonEncoder)))


def request_accept_json():
    return request.get_header('Accept') == 'application/json'


def is_active(url: str) -> str:
    params = request.query
    valid_keys = 'starred'
    valid_params = dict((k, v) for k, v in params.items() if k in valid_keys)
    full_path = urlunsplit(('', '', request.path, urlencode(valid_params), ''))
    return 'active' if full_path == url else ''


def favicon(id: str) -> str:
    file = str(id) + '.ico'
    path = 'feed.png'
    if os.path.exists(os.path.join('static', 'favicons', file)):
        path = 'favicons/' + file
    return url('/static/<filename:path>', filename=path)


def date_format(date: DateField) -> str:
    formatted = '--:--'
    if date:
        formatted = date.strftime('%H:%M') if (date.date() == datetime.today().date()) else date.strftime('%y-%m-%d')
    return formatted


@hook('before_request')
def connect():
    db.connect()


@hook('after_request')
def disconnect():
    if not db.is_closed():
        db.close()


@route('/')
def index():
    redirect(url('/items'))


@route('/channels/<id:int>/items', method='GET')
@route('/items', method='GET')
def items(id:int=None) -> str:
    valid_params = {'1': True, '0': False}
    starred = valid_params.get(request.query.getone('starred'))
    read = valid_params.get(request.query.getone('read'))

    channel = request.query.channel or id
    since_id = request.query.since_id
    max_id = request.query.max_id
    count = int(request.query.count) if request.query.count else 25
    page = int(request.query.page) if request.query.page else 1
    search = request.query.q
    
    query = Item.select()
    if channel:
        query = query.where(Item.channel == channel)
    if starred:
        query = query.where(Item.starred == starred)
    if read:
        query = query.where(Item.read == read)
    if since_id:
        query = query.where(Item.id >= since_id)
    if max_id:
        query = query.where(Item.id <= max_id)
    if search:
        search = '%' + search + '%'
        query = query.where(Item.title ** search | Item.description ** search | Item.author ** search)

    total_count = query.count()
    if page and count: query = query.paginate(page, count)

    out = {'items': list(query.order_by(Item.updated.desc()).limit(count))}

    channels = Channel.select().order_by(Channel.title)
    for c in channels:
        c.new = c.has_new()

    if channel:
        Item.update(new=False).where(Item.channel == channel).execute()

    params = request.query
    params['page'] = page + 1
    out['next'] = urlunsplit(('', '', request.fullpath, urlencode(params), '')) if page <= math.ceil(
        total_count / count) else None
    params['page'] = page - 1 if page > 1 else 1
    out['prev'] = urlunsplit(('', '', request.fullpath, urlencode(params), '')) if page > 1 else None

    if request_accept_json():
        return out
    else:
        return template('index', out, is_active=is_active, favicon=favicon, date_format=date_format, channels=channels)


@route('/items/<id:int>', method='GET')
def item(id:int) -> str:
    try:
        item = Item.get(Item.id == id)
    except Item.DoesNotExist:
        abort(404, 'Item does not exist')
    if request.get_header('Accept') == 'application/json':
        return {'item': item}
    else:
        return template('item', {'item': item})


@route('/items/<id:int>', method='PATCH')
def patch_item(id:int) -> str:
    try:
        item = Item.get(Item.id == id)
    except Item.DoesNotExist:
        abort(404)

    valid_keys = ['read', 'starred']
    for key in set(valid_keys).intersection(set(request.json.keys())):
        setattr(item, key, request.json[key])

    item.save()
    return response.status


@route("/channels", method='GET')
def channels() -> str:
    return {'channels': Channel.select()}


@route("/channels/<id:int>", method='GET')
def channel(id:int) -> str:
    try:
        channel = Channel.get(Channel.id == id)
    except Channel.DoesNotExist:
        abort(404, 'Channel does not exist')
    return {'channel': channel}


@route('/channels/<id:int>/delete', method='GET')
def delete_channel_confirm(id:int) -> str:
    try:
        channel = Channel.get(Channel.id == id)
    except Channel.DoesNotExist:
        abort(404, 'Channel does not exist')

    return template('delete', channel=channel)


@route('/channels/<id:int>', method='DELETE')
@route('/channels/<id:int>/delete', method='POST')
def delete_channel(id:int):
    try:
        channel = Channel.get(Channel.id == id)
        Item.delete().where(Item.channel == channel).execute()
        channel.delete_favicon()
        Channel.delete().where(Channel.id == id).execute()
    except Channel.DoesNotExist:
        abort(404, 'Channel does not exist')
    redirect(url('/'))


@route('/channels/create', method='GET')
def create_channel() -> str:
    return template('create')


@route('/channels', method='POST')
def post_channel():
    url = request.forms.get('url')
    Channel.create_from_url(url)
    channel = Channel.get(Channel.url == url)
    channel.save_favicon()
    channel.update_feed()
    redirect(url('/channels/<id:int>/items', id=channel.id))


@route('/channels/<id:int>/edit', method='GET')
def edit_channel(id:int) -> str:
    channel = Channel.get(Channel.id == id)
    return template('edit', channel=channel)


@route('/channels/<id:int>/edit', method='POST')
def edit_channel_post(id:int):
    title = request.forms.get('title')
    url = request.forms.get('url')
    channel = Channel.get(Channel.id == id)
    channel.title = title
    channel.url = url
    channel.save()
    redirect(url('/channels/<id:int>/items', id=channel.id))


@route('/channels/update', method='GET')
def update_channels():
    for channel in Channel.select():
        try:
            channel.update_feed()
        except:
            continue

    return redirect(url('/items'))


# possibly temporary route to update favicons for already established db's
@route('/channels/update-favicons', method='GET')
def update_channels():
    for c in Channel.select():
        try:
            c.save_favicon()
        except :
            continue

    return redirect(url('/items'))


@route('/channels/<id:int>/update', method='GET')
def update_channel(id: int):
    try:
        channel = Channel.get(Channel.id == id)
        channel.update_feed()
    except Channel.DoesNotExist:
        abort(404, 'Channel does not exist')
    return redirect(url('/channels/<id:int>/items', id=channel.id))


@route('/channels/import', method='GET')
def import_channels():
    return template('import')


@route('/channels/import', method='POST')
def import_channels_post():
    upload = request.files.get('file')
    Channel.create_from_file(upload.file)
    redirect(url('/items'))


@route('/static/<filename:path>')
def server_static(filename: str) -> Response:
    return static_file(filename, root='static/')


@route('/favicon.ico')
def get_favicon() -> Response:
    return server_static('favicon.ico')


if __name__ == '__main__':
    try:
        from mod_wsgi import version
    except:
        run(host='0.0.0.0', port=3000, reloader=True, debug=True)
