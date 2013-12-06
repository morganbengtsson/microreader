from bs4 import BeautifulSoup
import urllib.request


# TODO: try top domain if subdomain fails
def get_domain(url):
	parsed_uri = urllib.request.urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return domain

def open_url(url):
	req = urllib.request.Request(url) 
	req.add_header('User-Agent', 'Micro-reader Browser')	
	return urllib.request.urlopen(req)

def get_icon_link(domain):
	page = open_url(domain)
	soup = BeautifulSoup(page)
	icon_link = soup.find('link', rel='shortcut icon')
	if icon_link:
		return icon_link['href']

	return None

def write_icon(icon_link, save_as):
	icon = open_url(icon_link)
	with open(save_as, 'wb') as f:
		f.write(icon.read())

def save_favicon(url, save_as):
	print('saving url %s as %s' % (url, save_as))
	domain = get_domain(url)
	# direct link first
	try:
		write_icon(domain + 'favicon.ico', save_as)
	except Exception:
		print('no direct icon; trying to find link')
		icon_link = get_icon_link(domain)
		if icon_link:
			write_icon(icon_link, save_as)
		else:
			print('no icon link found')
	


