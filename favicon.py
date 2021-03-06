import os
import logging

try:
    from urllib.request import urlparse, Request, urlopen, urlretrieve
except ImportError:
    from urlparse import urlparse
    from urllib2 import Request, urlopen
    from urllib import urlretrieve
from bs4 import BeautifulSoup as bs

logging.basicConfig(level=logging.ERROR)


def get_icon_url(url):
    ''' looks for icon link directly at <url>/favicon.ico '''
    # try finding header link first
    page = open_url(url)
    if page and (page.getcode() == 200):
        try:
            tmp_url = None
            soup = bs(page)
            # actually this will fetch both 'shortcut icon' and 'icon'
            # icon_link = soup.find('link', rel='icon')
            # the lambda is to fix a bug in bs4 regarding case sensitivity
            icon_link = soup.find('link', rel=lambda x: x and x.lower() == 'icon')
            icon_url = icon_link['href']
            if icon_url:
                logging.debug('found header icon link: ' + icon_url)
                # get absolute url if relative
                page = open_url(icon_url)
                if not page or (page.getcode() != 200):
                    if icon_url.startswith('//'):
                        tmp_url = 'http:' + icon_url
                    elif icon_url.startswith('/'):
                        tmp_url = get_domain(url) + icon_url
                else:
                    tmp_url = icon_url
            # some sites actually have a dead link in header but a working direct link
            # return only if readable, if not fallback to direct link
            page = open_url(tmp_url)
            if page and (page.getcode() == 200):
                return tmp_url
            else:
                logging.debug('dead header link found, trying direct')
        except:
            logging.debug('no header link found, trying direct')

    url = "%s/favicon.ico" % url
    page = open_url(url)
    if page and (page.getcode() == 200):
        # check that we're not being redirected
        if 'favicon.ico' in page.geturl():
            return url

    return None


def get_feedburner_link(url):
    ''' read feedburner page and returns the "link" property
    which should contain a link back to the original site '''
    page = open_url(url)
    if page and (page.getcode() == 200):
        try:
            soup = bs(page)
            link = soup.link.string
            # alternative solution
            if not link:
                link = soup.find('link', rel='alternate')['href']
            logging.debug('link: %s' % link)
            return normalize_url(link)
        except:
            pass
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
    return parts[0][:start + 2] + '.'.join(parts[1:])


def normalize_url(url):
    if url.startswith("http://"):
        pass
    elif url.startswith("https://"):
        pass
    else:
        url = "http://%s" % url

    if url.endswith("/"):
        url = url[0:len(url) - 1]
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

    page = open_url(url)
    if page:
        try:
            with open(save_as, 'wb') as icon:
                icon.write(page.read())
            # file check
            if os.path.exists(save_as):
                size = os.path.getsize(save_as)
                if size < 100:
                    # file corrupted, lets trash it
                    logging.debug('icon corrupted')
                    os.remove(save_as)

        except:
            logging.debug('unable to retrieve url: ' + url)
    else:
        logging.debug('cannot read url: ' + url)


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
        logging.debug('flink: %s' % flink)
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
        logging.debug('retrieving url: ' + icon_url)
        retrieve_url(icon_url, save_as)
    else:
        logging.debug('no favicon found for url: [%s]' % url)


