import subprocess as sub
import functools
import asyncio
import socket
import time


def wait_eval_condition(condition, timeout, tick):
    startTime = time.time()
    ret = None
    while time.time()-startTime < timeout:
        ret = condition()
        if ret: 
            return ret
        time.sleep(tick)
    return None

def wait_condition(condition, timeout, tick):
    startTime = time.time()
    while time.time()-startTime < timeout:
        if condition():
            return True
        time.sleep(tick)
    return False

async def co_wait_condition(condition, timeout, tick):
    startTime = time.time()
    while time.time()-startTime < timeout:
        if condition():
            yield True
            return 
        await asyncio.sleep(tick)
    yield False

async def co_wait_co_condition(co_condition, timeout, tick):
    startTime = time.time()
    while time.time()-startTime < timeout:
        ret = await co_condition()
        if ret:
            yield True
            return
        await asyncio.sleep(tick)
    yield False

def is_socket_listening(address, timeout=10):
    if type(address) == tuple:
        family = socket.AF_INET
    elif type(address) == str:
        family = socket.AF_UNIX
    else:
        raise Exception('Check address')
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(timeout)
    r = s.connect_ex(address)
    s.close()
    return r == 0

def wait_socket_listening(address, timeout, tick, check_timeout):
    condition = functools.partial(is_socket_listening, address, timeout=check_timeout)
    return wait_condition(condition, timeout, tick)

def is_process_running(pattern, timeout=1):
    cmd = ['pgrep', '-f', pattern]
    try:
        ret = sub.check_output(cmd, timeout=timeout).decode('utf8')
        return bool(ret)
    except Exception:
        return False

def wait_process_started(pattern, timeout, tick, check_timeout):
    condition = functools.partial(is_process_running, pattern, timeout=check_timeout)
    return wait_condition(condition, timeout, tick)

def wait_process_ended(pattern, timeout, tick, check_timeout):
    condition = lambda: not is_process_running(pattern, check_timeout)
    return wait_condition(condition, timeout, tick)

def is_container_running(container_name, timeout=1):
    cmd = "docker inspect -f {{.State.Running}} `docker ps -aqf name=%s` || true" % container_name
    try:
        ret = sub.check_output(cmd, shell=True, stderr=sub.DEVNULL, timeout=timeout).decode('utf8').strip()
        return  ret == 'true'
    except Exception:
        return False

def wait_container_running(container_name, timeout, tick, check_timeout):
    condition = lambda: is_container_running(container_name, check_timeout)
    return wait_condition(condition, timeout, tick)
