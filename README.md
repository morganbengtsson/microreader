Very simple web based RSS/Atom reader, written in python and bottle. 

Try it out by installing requirements `pip install requirements.txt` and 
run `python microreader.py` . Then access http://localhost:3000

Runs on [Apache with mod_wsgi](http://bottlepy.org/docs/dev/deployment.html#apache-mod-wsgi).
an example app.wsgi is included in the repository.

A JSON api is available for most url:s, by adding 'application/json' 
to the Accept header.

![Microreader](http://morganbengtsson.github.io/images/microreader.png "Microreader")
