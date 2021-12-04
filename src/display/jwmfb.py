import subprocess as sub
import shutil
import os

from .wait import wait_socket_listening, wait_process_started


class Jwmfb:
    def __init__(self, config):
        self._config = config
        self._xvfb_pipe = None
        self._jwm_pipe = None
        num = self._config['display_number']
        self._fbdir = '/root/shared/fbdirs/%s' % num

    def up(self):
        self._write_jwmrc()
        self._honor_lock()
        self._open_xvfb()
        self._open_jwm()

    def down(self):
        if self._jwm_pipe:
            self._jwm_pipe.kill()
            self._jwm_pipe.communicate()
        else:
            sub.run("pkill jwm".split(), stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        if self._xvfb_pipe:
            self._xvfb_pipe.kill()
            self._xvfb_pipe.communicate()
        else:
            sub.run("pkill Xvfb".split(), stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        try:
            os.remove(self._fbdir + '/Xvfb_screen0')
        except Exception:
            pass

    def _write_jwmrc(self):
        path1 = '/root/jwmrc.tpl.xml'
        path2 = '/root/jwmrc.xml'
        with open(path1, 'r') as fd:
            s = fd.read()
        s = s.format(**self._config)
        with open(path2, 'w') as fd:
            fd.write(s)

    def _honor_lock(self):
        num = self._config['display_number']
        path = '/tmp/.X%s-lock' % num
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                raise Exception('display locked')

    def _open_xvfb(self):
        num = self._config['display_number']
        w = self._config['screen_width']
        h = self._config['screen_height']
        os.makedirs(self._fbdir, mode=0o755, exist_ok=True)
        socket_path  = '/tmp/.X11-unix/X%s' % num
        if os.path.exists(socket_path):
            try:
                os.remove(socket_path)
            except Exception:
                try:
                    shutil.rmtree(socket_path, ignore_errors=False)
                except Exception:
                    raise Exception('display locked')
        args = [
            'Xvfb', ':%s'%num, '-screen', '0', '%sx%sx24'%(w, h), '-nocursor',
            '-fbdir', self._fbdir,
        ]
        self._xvfb_pipe = sub.Popen(args, stdout=sub.PIPE)
        if not wait_socket_listening(socket_path, timeout=5, tick=0.1, check_timeout=0.5):
            raise Exception('cannot start xvfb')

    def _open_jwm(self):
        num = self._config['display_number']
        path = '/root/jwmrc.xml'
        args = ['jwm', '-display',  ':%s'%num, '-f', path]
        self._jwm_pipe = sub.Popen(args, stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        if not wait_process_started('jwm', timeout=5, tick=0.5, check_timeout=0.5):
            raise Exception('cannot start jwm')
