import json
import time
import uuid

from fastapi import APIRouter, Request, Response

from . import utils

router = APIRouter()


@router.get('/', description="returns some information about the engine such as the available spiders and the queue backlog count")
async def index(req: Request):
    return {
        'success': True,
        'message': 'under your service, sir :)',
        'payload': {
            'spiders': [spider_name for spider_name in req.app.x.spiders],
            'backlog': req.app.redis.llen(req.app.x.queue_name + '.BACKLOG')
        }
    }


@router.get('/run/{spider_name}', description="execute the specified spider in `{spider_name}` and wait for it to return its result, P.S: any query param will be passed to the spider as argument `-a key=value`")
@router.post('/run/{spider_name}', description="execute the specified spider in `{spider_name}` and wait for it to return its result, P.S: any query param and json post data will be passed to the spider as argument `-a key=value`")
async def run(spider_name: str, req: Request, res: Response):
    args = req.query_params._dict
    spider = req.app.x.spiders.get(spider_name, None)

    if not spider:
        res.status_code = 404
        return {
            'success': False,
            'error': 'no valid spider specified'
        }

    try:
        post_data = await req.json()
        if isinstance(post_data, dict):
            args = {**args, **post_data}
    except:
        pass

    result = utils.crawl(spider, req.app.x.settings, args)
    items = result.items
    stats = result.stats.get_stats()

    if stats.get('spider_exceptions/Exception', 0) > 0 and len(items) < 1:
        res.status_code = 500
        return {
            'success': False,
            'error': 'something went wrong, there may be an exception in your spider request',
            'payload': {
                'stats': stats,
                'items': items,
            }
        }

    return {
        'success': True,
        'payload': {
            'items': items,
            'stats': stats,
        }
    }


@router.get('/enqueue/{spider_name}', description="adding the specified spider in `{spider_name}` to the backlog to be executed later, P.S: any query param will be used as spider argument")
@router.post('/enqueue/{spider_name}', description="adding the specified spider in `{spider_name}` to the backlog to be executed later, P.S: any query param and json post data will be used as spider argument")
async def enqueue(spider_name: str, req: Request, res: Response):
    args = req.query_params._dict
    spider = req.app.x.spiders.get(spider_name, None)

    if not spider:
        res.status_code = 404
        return {
            'success': False,
            'error': 'invalid spider specified'
        }

    try:
        post_data = await req.json()
        if isinstance(post_data, dict):
            args = {**args, **post_data}
    except:
        pass

    args["created_at"] = int(time.time())
    args["jobid"] = str(uuid.uuid4())

    task = {
        'spider': spider_name,
        'args': args,
    }

    req.app.redis.rpush(
        req.app.x.queue_name + ".BACKLOG",
        json.dumps(task)
    )

    return {
        'success': True,
        'task': task,
    }
