import subprocess as sub
import numpy as np
import cv2 as cv
import random
import socket
import time
import mmap
import os

from .wait import wait_container_running, wait_condition
from .cutils import find_first_template
from .vnc import start_vnc
from . import xlibpy


DEFAULT_CONFIG = dict(
    display_number=1,
    screen_width=1366,
    screen_height=768,
    tray_height=25,
    window_border=4,
    window_title_height=21,
)


class Display:
    def __init__(self, display_number=None, config={}):
        c = DEFAULT_CONFIG.copy()
        c.update(config)
        self.config = c
        if display_number is not None:
            c['display_number'] = display_number
        self.display_number = c['display_number']
        self.screen_width = c['screen_width']
        self.screen_height = c['screen_height']
        self._buffer_file = None
        self._mmap = None
        self._mview = None

    def up(self):
        container_id = socket.gethostname()
        cmd = (
            "docker run --rm -d "
            "--name=jwmfb_{display_number} "
            "-v /root/app/mount:/root/app/mount "
            "--ipc=\"container:{container_id}\" "
            "dev.ru:90/jwmfb:1.0.0 "
            "jwmfb "
            "--display_number={display_number} "
            "--screen_width={screen_width} "
            "--screen_height={screen_height} "
            "--tray_height={tray_height} "
            "--window_border={window_border} "
            "--window_title_height={window_title_height} "
        ).format(container_id=container_id, **self.config)
        sub.Popen(cmd, shell=True, stdout=sub.DEVNULL, stderr=sub.DEVNULL)

        name = 'jwmfb_%s' % self.display_number
        if not wait_container_running(name, timeout=10, tick=0.5, check_timeout=5):
            raise Exception('cannot start xserver')

        cmd = (
            "docker "
            "exec jwmfb_{display_number} "
            "jwmfb-wait "
            "--display_number={display_number} "
            "--timeout=10.0"
        ).format(**self.config)
        try:
            sub.run(cmd.split(), check=True, timeout=15, stdout=sub.DEVNULL, 
                    stderr=sub.DEVNULL)
        except Exception:
            raise Exception('cannot start xserver')

        self.attach()


    def attach(self):
        if self.display_number != 0:
            fbpath = '/root/app/mount/jwmfb/fbdirs/%s/Xvfb_screen0' % self.display_number
            self._buffer_file = open(fbpath, 'rb') 
            self._mmap = mmap.mmap(self._buffer_file.fileno(), 0, prot=mmap.PROT_READ)
            self._mview = memoryview(self._mmap)
        xlibpy.deinit_display()
        xlibpy.init_display(self.display_number)

    def down(self):
        cmd = (
            "docker kill jwmfb_{}"
        ).format(self.display_number)
        sub.run(cmd.split(), timeout=10, stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        self.detach()

    def detach(self):
        if self._buffer_file:
            self._buffer_file.close()
        self._buffer_file = None
        self._mmap = None
        self._mview = None
        xlibpy.deinit_display()

    def show(self):
        host = os.environ.get('DOCKERHOST') or 'dev'
        start_vnc(host=host, display_number=self.display_number)

    def hide(self):
        cmd = "docker stop vncviewer"
        sub.run(cmd.split(), timeout=10, stdout=sub.DEVNULL, stderr=sub.DEVNULL)

    def shot(self, rect:'(x, y, w, h)')->'ci':
        x, y, w, h = rect[:4]
        buf = np.ndarray(
            (self.screen_height, self.screen_width, 4), 
            buffer=self._mview[202*16:], dtype='>u1'
        )
        i = buf[y:y+h, x:x+w]
        i = i[:, :, :3]
        i = i[:, :, ::-1]
        return i

    def mouse_position(self):
        return xlibpy.mouse_position()

    def mouse_move(self, point:'(x, y)', move_delay:'us'=300):
        xlibpy.mouse_move(point[0], point[1], move_delay)

    def mouse_click(self, button:'1..5', count=1, press_delay:'us'=10000, click_delay:'us'=10000):
        for n in range(count):
            xlibpy.mouse_click(button, press_delay)
            if n != count-1:
                time.sleep(click_delay//10**6)

    def clipboard_put(self, text):
        p = sub.Popen(
            "xsel -i -b --display :{}.0".format(self.display_number).split(),
            stdin=sub.PIPE, 
        )
        p.communicate(text.encode('utf8'), timeout=5)
        p.stdin.close()

    def clipboard_get(self)->str:
        p = sub.Popen(
            (
                "xsel -o -b --display :{}.0"
            ).format(self.display_number).split(),
            stdout=sub.PIPE,
        )
        text = p.communicate(timeout=5)[0].decode('utf8')
        return text

    def keyboard_type(self, text, delay:'ms'=50):
        sub.run(
            (
                "xdotool type --clearmodifiers --delay {}"
            ).format(delay).split() + [text],
            timeout=len(text)*2*delay+5,
            env={'DISPLAY':':%s.0'%self.display_number},
        )

    def keyboard_keys(self, *keys, delay:'ms'=50):
        sub.run(
            (
                "xdotool key --delay {}"
            ).format(delay).split() + list(keys),
            timeout=len(keys)*2*delay+5,
            env={'DISPLAY':':%s.0'%self.display_number},
        )

    def click_point(self, point, move_delay:'us'=300, button=1, count=1, 
                    press_delay:'us'=10000, click_delay:'us'=10000):
        self.mouse_move(point, move_delay=move_delay)
        self.mouse_click(button=button, count=count, 
                         press_delay=press_delay, click_delay=click_delay)


    def click_rect(self, rect:'(x, y, w, h)', button=1, count=1,  
                   press_delay:'us'=10000, click_delay:'us'=10000, 
                   move_delay:'us'=300, click_box=(0.4, 0.6)):
        x, y, w, h = rect[:4]
        x += random.randint(int(w*click_box[0]), int(w*click_box[1]))
        y += random.randint(int(h*click_box[0]), int(h*click_box[1]))
        self.mouse_move((x, y), move_delay)
        self.mouse_click(button=1, press_delay=press_delay, click_delay=click_delay) 
        
    def click_change(self, rect:'(x,y,w,h)', 
                     element:'(tpl,pt,d) or []', attempts=1, timeout=5, tick=0.5,
                     method='wait_match_template',
                     button=1, count=1,
                     press_delay:'us'=10000, click_delay:'us'=10000, 
                     move_delay:'us'=300):
        if isinstance(method, str):
            method_name = method
            method = lambda : getattr(self, method_name)(element, timeout, tick)
        for attempt in range(attempts):
            self.click_rect(
                rect=rect, button=button, count=count, press_delay=press_delay,
                click_delay=click_delay, move_delay=move_delay
            )
            if method():
                return 
        raise Exception('no_change')

    def match_template(self, template:'ci', topleft_point:'(x,y)', 
                       distance=0.0)->bool:
        template = _load_template(template)
        h, w = template.shape[:2]
        x, y = topleft_point
        image = self.shot((x, y, w, h))
        if distance == 0.0:
            return bool(find_first_template(template, image))
        else:
            ret = cv.matchTemplate(image, template, cv.TM_SQDIFF_NORMED)
            minval, _, _, _ = cv.minMaxLoc(ret)
            return minval < distance

    def find_template(self, template:'ci', search_rect:'(x,y,w,h)'=None, 
                      distance=0.0)->'(x,y)':
        template = _load_template(template)
        if search_rect is None:
            search_rect = 0, 0, self.screen_width, self.screen_height
        image = self.shot(search_rect)
        if distance == 0.0:
            ret = find_first_template(template, image)
            if ret:
                x = ret[0]+search_rect[0]
                y = ret[1]+search_rect[1]
                return x, y
            else:
                return None
        else:
            ret = cv.matchTemplate(image, template, cv.TM_SQDIFF_NORMED)
            minval, _, minloc, _ = cv.minMaxLoc(ret)
            if minval < distance:
                x = minloc[0]+search_rect[0]
                y = minloc[1]+search_rect[1]
                return x, y
            else:
                return None

    def match_phash(self, phash, topleft_point, distance=0):
        raise NotImplementedError()

    def find_phash(self, phash, search_rect, distance=0):
        raise NotImplementedError()

    def get_template_size(self, path):
        if path not in _template_cache:
            _load_template(path)
        i = _template_cache[path]
        h, w = i.shape[:2]
        return w, h

    ### dev utils ###
    def savetp(self, rect, name):
        path = '/root/app/mount/devdisp/%s.png' % name
        i = self.shot(rect)
        cv.imwrite(path, i[:, :, ::-1])
    
    s = savetp

    def showtp(self, rect):
        from PIL import Image
        i = self.shot(rect)
        Image.fromarray(i).show()

    sh = showtp

    def distance(self, template:'ci', topleft_point:'(x,y)'):
        template = _load_template(template)
        h, w = template.shape[:2]
        x, y = topleft_point
        image = self.shot((x, y, w, h))
        ret = cv.matchTemplate(image, template, cv.TM_SQDIFF_NORMED)
        minval, _, _, _ = cv.minMaxLoc(ret)
        return minval

    pos = mouse_position
    ktype = keyboard_type
    kk = keyboard_keys

    ### wait and assert ###
    '''
    Examples
    d.wait_match_template(element=('/path/name.png', (10, 20)), timeout=10, tick=0.5)
    d.wait_match_template((/path/name.png', (10, 20)), 10, 0.5)
    d.wait_neither_find_template([(/path/name1.png', (10, 20), ('/path/name2.png', (50, 60))), 10, 0.5)
    d.assert_match_template(('/path/name.png', (10, 20)), 10, 0.5)
    d.assert_any_match_phash([(/path/name1.png', (10, 20), ('/path/name2.png', (50, 60))), 10, 0.5)

    '''
    _prefices = (
        'wait_no_', 'wait_any_', 'wait_all_', 'wait_neither_', 'wait_',
        'assert_no_', 'assert_any_', 'assert_all_', 'assert_neither_', 'assert_',
    )
    def __getattr__(self, k):
        if not k.startswith(self._prefices):
            raise AttributeError(k)
        for prefix in self._prefices:
            if k.startswith(prefix):
                break
        if prefix.startswith('wait_'):
            return self._get_wait_func(k, prefix)
        else:
            k = 'wait'+k[6:]
            prefix = 'wait'+prefix[6:]
            wait_func = self._get_wait_func(k, prefix)
            def assert_func(*args):
                if wait_func(*args):
                    return
                else:
                    raise Exception('not asserted: %s: %s' % (k, args[0]))
            return assert_func

    def _get_wait_func(self, k, prefix):
        name = k[len(prefix):]
        method = object.__getattribute__(self, name)
        if prefix == 'wait_':
            def func(*args):
                element, timeout, tick = args
                condition = lambda : method(*element)
                return wait_condition(condition, timeout, tick)
        elif prefix == 'wait_no_':
            def func(*args):
                element, timeout, tick = args
                condition = lambda : not method(*element)
                return wait_condition(condition, timeout, tick)
        elif prefix == 'wait_any_':
            def func(*args):
                elements, timeout, tick = args
                def condition():
                    for element in elements:
                        if method(*element):
                            return True
                    return False
                return wait_condition(condition, timeout, tick)
        elif prefix == 'wait_all_':
            def func(*args):
                elements, timeout, tick = args
                def condition():
                    matched = True
                    for element in elements:
                        if not method(*element):
                            matched = False
                    return matched
                return wait_condition(condition, timeout, tick)
        elif prefix == 'wait_neither_':
            def func(*args):
                elements, timeout, tick = args
                def condition():
                    for element in elements:
                        if method(*element):
                            return False
                    return True
                return wait_condition(condition, timeout, tick)
        return func



_template_cache = {}
def _load_template(inp):
    global _template_cache
    if isinstance(inp, np.ndarray):
        return inp
    elif isinstance(inp, str):
        if inp in _template_cache:
            return _template_cache[inp]
        path = inp
        i = cv.imread(path)
        if i is None:
            raise Exception('cannot load template: %s' % path)
        i = i[:, :, ::-1]
        _template_cache[inp] = i
        return i
    else:
        raise Exception('bad_template')
