import os, logging
from bs4 import BeautifulSoup
try: 
	from urllib.request	 import urlparse, Request, urlopen, urlretrieve
except ImportError:
	from urlparse import urlparse
	from urllib2 import Request, urlopen, urlretrieve

logging.basicConfig(level=logging.DEBUG)	

def get_domain(url):
	if not url.startswith('http://'):
		url = 'http://' + url
	return 'http://' + url.split('/')[2]

def open_url(url):
	req = Request(url) 
	req.add_header('User-Agent', 'Micro-reader Browser')	
	return urlopen(req)

def get_icon_link(domain):
	try:
		page = open_url(domain)
		soup = BeautifulSoup(page)
		icon_link = soup.find('link', rel='shortcut icon')
		if icon_link:
			return icon_link['href']
		else:
			return None
	except:
		logging.debug('favicon: get_icon_link failed')
		return None

def get_feedburner_link(url):
	page = open_url(url)
	soup = BeautifulSoup(page)
	return soup.link.string

def write_icon(icon_link, save_as):
	urlretrieve(icon_link, save_as)

def save_favicon(url, save_as, one_up=False):
	logging.debug('saving url %s as %s' % (url, save_as))
	if os.path.exists(save_as):
		logging.debug('favicon: ' + save_as + ' already exists')
		return
	if not one_up:	
		url = get_domain(url)

	# special handling for feedburner
	if 'feedburner.com' in url:
		logging.debug('got feedburner url')
		url = get_domain(get_feedburner_link(url)) 
	logging.debug('domain:', url)

	# create save dir
	if not os.path.exists(os.path.dirname(save_as)):
		os.mkdir(os.path.dirname(save_as))
	
	try: # direct link first
		write_icon(url + 'favicon.ico', save_as)
	except:
		logging.debug('no direct icon; trying to find link')
		icon_link = get_icon_link(url)
		if icon_link:
			write_icon(icon_link, save_as)
		else:
			if not one_up: # try parent domain
				logging.debug('no icon link found, trying top level')
				top = 'http://' + '.'.join(url.split('.')[1:]) + '/'
				save_favicon(top, save_as, True)
			else:
				logging.debug('giving up')
	


