import os, logging
from bs4 import BeautifulSoup as bs
try: 
	from urllib.request	 import urlparse, Request, urlopen, urlretrieve
except ImportError:
	from urlparse import urlparse
	from urllib2 import Request, urlopen, urlretrieve

logging.basicConfig(level=logging.DEBUG)

def get_icon_url(url):
	''' looks for icon link directly at <url>/favicon.ico '''
	url = "%s/favicon.ico" % url
	page = open_url(url)
	if page:
		if page.getcode() == 200:
			return url

	return None

def get_feedburner_link(url):
	''' read feedburner page and returns the "link" property 
	which should contain a link back to the original site '''
	page = open_url(url)
	if page:
		soup = bs(page)
		return soup.link.string
	return None

def get_domain(url):
	''' http://domain.com/some/page.html => http://domain.com '''
	parts = url.split('/')
	return parts[0] + '//' + parts[2]

def get_superdomain(domain):
	''' http://sub.super.com => http://super.com (half-guessing without a TLD list)'''
	parts = domain.split('.')
	# already at top?
	if len(parts) <= 2:
		return None
	start = parts[0].find('//')
	return parts[0][:start+2] + '.'.join(parts[1:])

def normalize_url(url):
	if url.startswith("http://"):
		pass
	elif url.startswith("https://"):
		pass
	else:
		url = "http://%s" % url

	if url.endswith("/"):
		url = url[0:len(url)-1]
	return url

def open_url(url):
	''' open a url for reading '''
	try:
		req = Request(url)
		# need a custom user-agent to avoid bot blocking
		req.add_header('User-Agent', 'Micro-reader Browser')	
		return urlopen(req)
	except:
		return None

def retrieve_url(url, save_as):
	''' writes the file to disk '''
	# create save dir if missing
	if not os.path.exists(os.path.dirname(save_as)):
		os.mkdir(os.path.dirname(save_as))
	try:
		urlretrieve(url, save_as)
	except:
		logging.debug('unable to retrieve url: ' + url)

def save_favicon(url, save_as):
	# exists?
	if os.path.exists(save_as):
		logging.debug('favicon: ' + save_as + ' already exists')
		return

	icon_url = None
	url = normalize_url(url)
	# check if feedburner
	if 'feedburner.com' in url:
		flink = get_feedburner_link(url)
		# logging.debug('flink: ' + flink)
		if flink:
			icon_url = get_icon_url(flink)
	else:		
		# first get domain
		domain = get_domain(url)
		if domain:
			icon_url = get_icon_url(domain)
			if not icon_url:
				# try superdomain
				sdomain = get_superdomain(domain)
				icon_url = get_icon_url(sdomain)

	if icon_url:
		retrieve_url(icon_url, save_as)
	else:
		logging.debug('no favicon found for url: [%s]' % url)


