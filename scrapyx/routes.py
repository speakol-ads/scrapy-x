import json
import queue
import socket
import time
import uuid

import joblib
from fastapi import APIRouter, Request, Response

from . import utils

router = APIRouter()


@router.get('/', description="returns some information about the engine such as the available spiders and the queue backlog count")
async def index(req: Request):
    return await daemonstatus(req)


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

    if req.method.lower() == 'post':
        try:
            post_data = await req.json()
            if isinstance(post_data, dict):
                args = {**args, **post_data}
        except Exception as e:
            res.status_code = 400
            return {
                'success': False,
                'error': str(e)
            }

    args["created_at"] = int(time.time())
    args["jobid"] = str(uuid.uuid4())

    result = utils.crawl(spider, req.app.x.settings, args)
    items = result.items
    stats = result.stats.get_stats()

    if stats.get('spider_exceptions/Exception', 0) > 0 and len(items) < 1:
        res.status_code = 500
        return {
            'success': False,
            'error': 'something went wrong, there may be an exception in your spider request',
            'payload': {
                'jobid': args['jobid'],
                'items': items,
            }
        }

    return {
        'success': True,
        'payload': {
            'jobid': args['jobid'],
            'items': items,
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

    if req.method.lower() == 'post':
        try:
            post_data = await req.json()
            if isinstance(post_data, dict):
                args = {**args, **post_data}
        except Exception as e:
            res.status_code = 400
            return {
                'success': False,
                'error': str(e)
            }

    args["created_at"] = int(time.time())
    args["jobid"] = str(uuid.uuid4())

    task = {
        'spider': spider_name,
        'args': args,
    }

    req.app.x.redis_conn.rpush(
        req.app.x.queue_backlog_names[spider_name],
        json.dumps(task)
    )

    return {
        'success': True,
        'payload': task,
    }


@router.get("/daemonstatus.json", description="scrapyd compatible endpoint")
async def daemonstatus(req: Request):
    pending = {}
    finished = {}
    rpm = {}

    for queue_name, full_name in req.app.x.queue_backlog_names.items():
        pending[queue_name] = req.app.x.redis_conn.llen(full_name)

    for queue_name, full_name in req.app.x.queue_finished_counter_names.items():
        finished[queue_name] = int(req.app.x.redis_conn.get(full_name) or 0)

    for queue_name, full_name in req.app.x.queue_consumers_rpm_names.items():
        rpm[queue_name] = int(req.app.x.redis_conn.get(full_name) or 0)

    return {
        "status": "ok",
        "pending": sum(pending.values()),
        "finished": sum(finished.values()),
        "rpm": sum(rpm.values()),
        "details": {
            "pending": pending,
            "finished": finished,
            "rpm": rpm
        },
        "node_name": socket.gethostname(),
    }


@router.get("/schedule.json", description="scrapyd compatible endpoint")
@router.post("/schedule.json", description="scrapyd compatible endpoint")
async def schedule(req: Request, res: Response):
    result = await enqueue(
        req.query_params.get("spider", None),
        req,
        res
    )

    if result["success"]:
        return {
            "status": "ok",
            "jobid": result["payload"]["args"]["jobid"],
        }

    return {"status": "error"}


@router.post('/batch/enqueue/{spider_name}', description="adding the specified spider in `{spider_name}` to the backlog to be executed later on multiple items, P.S: any query param and json post data will be used as spider argument")
async def batch_enqueue(spider_name: str, req: Request, res: Response):
    spider = req.app.x.spiders.get(spider_name, None)

    if not spider:
        res.status_code = 404
        return {
            'success': False,
            'error': 'invalid spider specified'
        }

    try:
        post_data = list(await req.json())
        if not isinstance(post_data, list):
            res.status_code = 400
            return {
                'success': False,
                'error': 'invalid post data spcified, it should be a list'
            }
    except Exception as e:
        res.status_code = 500
        return {
            'success': False,
            'error': str(e)
        }

    tasks = []

    for item in post_data:
        args = item
        args["created_at"] = int(time.time())
        args["jobid"] = str(uuid.uuid4())

        task = {
            'spider': spider_name,
            'args': args,
        }

        req.app.x.redis_conn.rpush(
            req.app.x.queue_backlog_names[spider_name],
            json.dumps(task)
        )

        tasks.append(task)

    return {
        'success': True,
        'payload': tasks,
    }
