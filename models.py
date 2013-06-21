import feedparser
from peewee import *
import lxml.html as ht
import xml.etree.ElementTree as ET
from datetime import datetime
from time import mktime

db = SqliteDatabase('database.db')

class BaseModel(Model):
	class Meta:
		database = db

class Channel(BaseModel):
	title = TextField()
	updated = DateTimeField(null = True)
	fetched = DateTimeField(default = datetime.now())
	url = TextField(unique = True)
	icon = TextField(default = '/static/feed.png')
			
	def unread_count(self):
		return self.items.where(Item.read == False).count()
		
	def update_feed(self):
			feed = feedparser.parse(self.url)
			for entry in feed.entries:				
				updated = datetime(*entry.updated_parsed[:6]) if entry.updated_parsed else None
							
				description = entry.content[0].value if hasattr(entry, 'content') else entry.description
				description = ht.fromstring(description).text_content()
				
				parameters = dict(updated = updated, 
								  title = ht.fromstring(entry.get('title', 'No title')).text_content(), 
								  description = description, author = entry.get('author'), 
								  url = entry.get('link', 'No url'), channel = self)
				if not Item.select().where(Item.url == entry.link).exists():						
					Item.create(**parameters)
				else:
					Item.update(**parameters).where(Item.url == entry.link).execute()			
			
			self.updated = datetime(*feed.updated_parsed[:6]) if 'updated_parsed' in feed else None
			
			self.fetched = datetime.now()
			self.save()
			
	@classmethod
	def create_from_url(cls, url):
		feed = feedparser.parse(url).feed					
		updated = datetime(*feed.updated_parsed[:6]) if 'updated_parsed' in feed else None	
		cls.create(url = url, updated = updated, title = feed.get('title', 'No title')) 
				
	class FeedDoesNotExist(Exception) : pass
	
class Item(BaseModel):
	title = TextField()
	description = TextField()
	author = TextField(null = True)
	url = TextField(unique = True)
	read = BooleanField(default = False)
	starred = BooleanField(default = False)
	channel = ForeignKeyField(Channel, cascade = True, related_name = 'items')
	updated = DateTimeField(null = True)
	fetched = DateTimeField(default = datetime.now())

	
Channel.create_table(fail_silently = True)
if not Channel.select().where(Channel.url == "http://rss.slashdot.org/Slashdot/slashdot").exists():
	Channel.create_from_url("http://rss.slashdot.org/Slashdot/slashdot")
Item.create_table(fail_silently = True)
