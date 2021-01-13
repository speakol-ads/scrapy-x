
scrapy-x (X)
=============
> a very simple scrapy subcommand which makes scrapy a very simple distributed high-performance scraping framework

Installation
============
```bash
$ pip install -U scrapy-x
```

Usage
======
> let's assume that you have a project called `TestCrawler`
- cd to `TestCrawler`
- run `scrapy x`
- that is all!

Default Settings
================
> it utilizes your default project `settings.py` file  

```python  

# whether to enable debug mode or not
X_DEBUG = True

# the default queue name that the system will use
# actually it will be used as a prefix for its internal
# queues, currently there is only one queue called `X_QUEUE_NAME + '.BACKLOG'`
# which holds all jobs that should be crawled.
X_QUEUE_NAME = 'SCRAPY_X_QUEUE'

# the queue workers
# by default it uses the cpu cores count
# try to adjust it based on your resources & needs
X_QUEUE_WORKERS_COUNT = os.cpu_count()

# the webserver workers count
# the workers count required from uvicorn to spwan
# defaults to the available cpu count
# try to adjust it based on your resources & needs
X_SERVER_WORKERS_COUNT = os.cpu_count()

# the port the http server should listen on
X_SERVER_LISTEN_PORT = 6800

# the host used by the http server to listen on
X_SERVER_LISTEN_HOST = '0.0.0.0'

# whether to enable access log or not
X_ENABLE_ACCESS_LOG = True

# redis host
X_REDIS_HOST = 'localhost'

# redis port
X_REDIS_PORT = 6379

# redis db
X_REDIS_DB = 0

# redis password
X_REDIS_PASSWORD = ''
```

Available Endpoints
=====================

**GET /**
> returns some info about the engine like the available spiders and backlog queue length

**GET|POST /run/{spider_name}**
> execute the specified spider in `{spider_name}` and wait for it to return its result, P.S: any query param and json post data will be passed to the spider as argument `-a key=value`



**GET|POST /enqueue/{spider_name}**
> adding the specified spider in `{spider_name}` to the backlog to be executed later, P.S: any query param and json post data will be used as spider argument

Technologies Used
=================
- [fastapi](https://fastapi.tiangolo.com/)
- [redis](https://redis.io)
- [scrapydo](https://github.com/rmax/scrapydo)
- [coloredlogs](https://pypi.org/project/coloredlogs/)

Author
======
> I'm Mohamed, a software engineer who enjoys writing code in his free time, I'm speaking python, php, go, rust and js

My Similar Projects
==================
- [scrapyr](https://github.com/alash3al/scrapyr)
- [scrapyly](https://github.com/alash3al/scraply)

**P.S**: star the project if you liked it ^_^
