import feedparser, listparser, favicon, os
from peewee import *
from bs4 import BeautifulSoup as bs
from datetime import datetime
from time import mktime

db = SqliteDatabase('database.db', threadlocals=True, timeout = 5000)
#db = MySQLDatabase('microreader', user = 'microreader', passwd='...', threadlocals=True, timeout = 5000)

def strip_tags(xml):
	if xml is None:
		return None
	else:
		return ''.join(bs(xml).findAll(text=True)) 

def get_updated(entity):
	if entity.has_key('published_parsed'):
		if entity.get('published_parsed'):
			return datetime.fromtimestamp(mktime(entity.published_parsed))
	return None

class BaseModel(Model):
	class Meta:
		database = db

class Channel(BaseModel):
	title = TextField()
	updated = DateTimeField(null = True)
	fetched = DateTimeField(default = datetime.now())
	url = TextField()
	icon = TextField(default = '/static/feed.png')
	
	def has_new(self):
		return True if (self.items.where(Item.new == True).count() > 0) else False
					
	def unread_count(self):
		return self.items.where(Item.read == False).count()
		
	def update_feed(self):
			feed = feedparser.parse(self.url)
			for entry in feed.entries:				
				updated = get_updated(entry)
							
				description = entry.content[0].value if hasattr(entry, 'content') else entry.description		
				description_text = strip_tags(description)								
				description_html = bs(description).prettify()

				# temp fix for enclosures
				enclosures = entry.get('enclosures')
				if enclosures:
					for enclosure in enclosures:
						description_html += '<hr/><a href="' + enclosure['href'] + '">' + enclosure['href'] + '</a>'

				# fix for feeds without item urls
				url_guid = entry.get('link', None)
				if not url_guid:
					url_guid =  entry.get('guid', 'No url')
				
				parameters = dict(updated = updated, 
								  title = strip_tags(entry.get('title', 'No title')), 
								  description = description_text, 
								  description_html = description_html,
								  author = entry.get('author'), 
								  url = url_guid, 
								  channel = self)
				if not Item.select().where(Item.url == url_guid).exists():						
					Item.create(**parameters)
				else:
					Item.update(**parameters).where(Item.url == url_guid).execute()			
			
			self.updated = get_updated(feed)
			# use author as channel title if untitled
			if self.title == 'Untitled':
				if len(feed.entries):
					title = feed.entries[0].get('author')
					if title and title.strip():
						self.title = title
			self.fetched = datetime.now()
			self.save()
	
	def save_favicon(self):		
		icon_path = os.path.join('static', 'favicons', str(self.id) + '.ico')
		favicon.save_favicon(self.url, icon_path)

	def delete_favicon(self):
		icon_path = os.path.join('static', 'favicons', str(self.id) + '.ico')
		if os.path.exists(icon_path):
			os.remove(icon_path)
			
	@classmethod
	def create_from_url(cls, url):
		feed = feedparser.parse(url).feed	
		updated = get_updated(feed)
		title = feed.get('title', 'Untitled')
		if not title.strip():
			title = 'Untitled'
		cls.create(url = url, updated = updated, title = title) 
	
	@classmethod
	def create_from_file(cls, file):
		opml = listparser.parse(file)
		print('found %s feeds' % (len(opml.feeds)))
		for feed in opml.feeds:
			cls.create(url = feed.url, title = feed.title)
	
			
	class SaveFavicon(Exception) : pass			
	class FeedDoesNotExist(Exception) : pass
	
class Item(BaseModel):
	title = TextField()
	description = TextField()
	description_html = TextField()
	author = TextField(null = True)
	url = TextField(unique = True)
	read = BooleanField(default = False)
	new = BooleanField(default = True)
	starred = BooleanField(default = False)
	channel = ForeignKeyField(Channel, on_delete='cascade', related_name = 'items')
	updated = DateTimeField(null = True)
	fetched = DateTimeField(default = datetime.now())

	
Channel.create_table(fail_silently = True)
Item.create_table(fail_silently = True)

if not Channel.select(Channel.url).count():
	if not Channel.select().where(Channel.url == "http://rss.slashdot.org/Slashdot/slashdot").exists():
		Channel.create_from_url("http://rss.slashdot.org/Slashdot/slashdot")
