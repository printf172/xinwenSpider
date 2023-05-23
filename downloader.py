import traceback

import aiohttp
from loguru import logger


async def download(req, session=None, retry=3):
    kwargs = {}
    url = req["url"]
    headers = req["headers"]
    proxies = req.get("proxies", {})
    meta = req["meta"]
    method = req.get("method", "GET")
    timeout = req.get("timeout", 10)
    cookies = req.get("cookies", {})
    data = req.get("data", {})
    kwargs['headers'] = headers
    kwargs['timeout'] = timeout
    proxy = ""
    req_status = False
    if proxies:
        if "http" not in proxies["http"]:
            proxy = "http://" + proxies["http"]
        else:
            proxy = proxies["http"]
    if cookies:
        kwargs["cookies"] = cookies
    if not session:
        session = aiohttp.ClientSession()
    try:
        if method == "POST":
            logger.debug(f'post的数据 : {data}')
            response = await session.post(url, data=data, **kwargs)
        else:
            response = await session.get(url, **kwargs, proxy=proxy)
        status_code = response.status
        response_ = await response.text()
        meta["status_code"] = status_code
        req_status = True
        return response_, meta
    except aiohttp.client.ClientConnectorError as f:
        logger.error(f"链接失败 {f}")
    except aiohttp.ClientTimeout as f:
        logger.error(f"超时错误 {f}")
    except Exception as f:
        logger.error(f"error {f}")
        logger.error(f"{traceback.print_exc()}")
    finally:
        if not req_status:
            if retry < 2:
                retry += 1
                await download(req, retry=retry)
            return None, None
