import os
from bs4 import BeautifulSoup
try: 
	from urllib.request	 import urlparse, Request, urlopen
except ImportError:
	from urlparse import urlparse
	from urllib2 import Request, urlopen

# TODO: try top domain if subdomain fails
def get_domain(url, toplevel=False):
	parsed_uri = urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return domain

def open_url(url):
	req = Request(url) 
	req.add_header('User-Agent', 'Micro-reader Browser')	
	return urlopen(req)

def get_icon_link(domain):
	page = open_url(domain)
	soup = BeautifulSoup(page)
	icon_link = soup.find('link', rel='shortcut icon')
	if icon_link:
		return icon_link['href']

	return None

def get_feedburner_link(url):
	page = open_url(url)
	soup = BeautifulSoup(page)
	return soup.link.string

def write_icon(icon_link, save_as):
	icon = open_url(icon_link)
	with open(save_as, 'wb') as f:
		f.write(icon.read()) # TODO: check for errors

def save_favicon(url, save_as):
	print('saving url %s as %s' % (url, save_as))
	domain = get_domain(url)
	# special handling for feedburner
	if 'feedburner.com' in domain:
		print('got feedburner url')
		domain = get_domain(get_feedburner_link(url)) 
	print('domain:', domain)
	if not os.path.exists(os.path.dirname(save_as)):
		os.mkdir(os.path.dirname(save_as))
	
	try: # direct link first
		write_icon(domain + 'favicon.ico', save_as)
	except Exception:
		print('no direct icon; trying to find link')
		icon_link = get_icon_link(domain)
		if icon_link:
			write_icon(icon_link, save_as)
		else:
			print('no icon link found, trying top level')
			top = 'http://' + '.'.join(domain.split('.')[1:])
			save_favicon(top, save_as)
	


