 """Utility helpers for osint_pro"""
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Callable
import socket
import time
import logging

import requests

from . import config

logger = logging.getLogger("osint_pro.utils")
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "osint-pro/1.0"})
EXECUTOR = ThreadPoolExecutor(max_workers=config.MAX_THREADS)


def safe_get_json(url: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None, retries: int = 2) -> Optional[Any]:
    """Safely fetch JSON with retries."""
    t = timeout or config.DEFAULT_TIMEOUT
    last_exc = None
    for _ in range(retries + 1):
        try:
            r = SESSION.get(url, params=params, timeout=t)
            if r.status_code == 200:
                try:
                    return r.json()
                except Exception:
                    return None
            last_exc = Exception(f"status {r.status_code}")
        except Exception as e:
            last_exc = e
            logger.debug("safe_get_json error: %s", e)
        time.sleep(0.3)
    logger.debug("safe_get_json failed for %s: %s", url, last_exc)
    return None


def safe_post_text(url: str, data: Dict[str, Any], timeout: Optional[int] = None) -> Optional[str]:
    """Safely POST and return text."""
    t = timeout or config.DEFAULT_TIMEOUT
    try:
        r = SESSION.post(url, data=data, timeout=t)
        if r.status_code in (200, 203, 204, 302):
            return r.text
    except Exception as e:
        logger.debug("safe_post_text error: %s", e)
    return None


def is_ip(val: str) -> bool:
    """Check if val is IPv4 or IPv6."""
    for af in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(af, val)
            return True
        except Exception:
            continue
    return False


def run_blocking(func: Callable, *args, **kwargs):
    """Run blocking function in thread and return result."""
    fut = EXECUTOR.submit(func, *args, **kwargs)
    return fut.result()