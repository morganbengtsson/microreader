Microreader is a simple, lightweight and hackable self hosted RSS/Atom reader.
Written in [Python](http://python.org/) with help of the web framework [Bottle](http://bottlepy.org/), 
and the orm [Peewee](https://github.com/coleifer/peewee). 

Try it out by installing requirements `pip install -r requirements.txt` and 
run `python microreader.py` . Then access http://localhost:3000.

Runs on [Apache with mod_wsgi](http://bottlepy.org/docs/dev/deployment.html#apache-mod-wsgi).
An example app.wsgi is included in the repository.

To have automatic aggregation of feeds every twenty minutes, enter the 
following into crontab:
`*/20 * * * * wget -O - -q -t 1  http://<host>:<port>/channels/update`. 
Replace `<host>` and `<port>` with corresponding values.

A JSON api is available for most url:s, by adding `application/json`
to the Accept header.

[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/75b5f7c4e3722ff84d2f46e14dba6590 "githalytics.com")](http://githalytics.com/morganbengtsson/Micro-reader)

![Microreader](https://raw.github.com/morganbengtsson/morganbengtsson.github.com/master/images/microreader.png "Microreader")
