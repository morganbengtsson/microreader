Microreader is a simple, lightweight and hackable self hosted RSS/Atom reader.
Written in [Python](http://python.org/) with help of the web framework [Bottle](http://bottlepy.org/), 
and the orm [Peewee](https://github.com/coleifer/peewee). Microreader requires at least Python version 3.

Try it out by installing requirements `pip install -r requirements.txt` and 
run `python microreader.py` . Then access http://localhost:3000. In some environments
pip for Python 3 may have another alias, such as `pip3` or `pip-3.X` or similar.

Runs on [Apache with mod_wsgi](http://bottlepy.org/docs/dev/deployment.html#apache-mod-wsgi).
An example app.wsgi is included in the repository.

To have automatic aggregation of feeds every twenty minutes, enter the 
following into crontab:
`*/20 * * * * wget -O - -q -t 1  http://<host>:<port>/channels/update`. 
Replace `<host>` and `<port>` with corresponding values.

A JSON api is available for most url:s, by adding `application/json`
to the Accept header.

![Chrome](https://raw.github.com/morganbengtsson/Micro-reader/master/screenshots/chrome.png "Microreader in Chrome")
![Lynx](https://raw.github.com/morganbengtsson/Micro-reader/master/screenshots/lynx.png "Microreader in Lynx")
