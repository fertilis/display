import subprocess as sub
import time
import os

from .wait import wait_socket_listening, is_socket_listening

PORT = 5900

class Vnc:
    def __init__(self, display_number=1, scale='1.0', viewonly=False, 
                 fullscreen=False, timeout=None):
        self._display_number = display_number
        self._scale = scale
        self._viewonly = viewonly
        self._fullscreen = fullscreen
        self._timeout = timeout or 30
        self._x11vnc_pipe = None
        self._vncviewer_pipe = None

    def up(self):
        address = ('', PORT)
        if not is_socket_listening(address, 5):
            self._start_server()
        time.sleep(0.1)
        self._start_client()

    def down(self):
        if self._vncviewer_pipe:
            self._vncviewer_pipe.terminate()
            try:
                self._vncviewer_pipe.wait(timeout=1)
            except Exception:
                self._vncviewer_pipe.kill()
            self._vncviewer_pipe.communicate()
        else:
            sub.run('pkill vncviewer'.split(), 
                    stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        if self._x11vnc_pipe:
            self._x11vnc_pipe.terminate()
            try:
                self._x11vnc_pipe.wait(timeout=1)
            except Exception:
                self._x11vnc_pipe.kill()
            self._x11vnc_pipe.communicate()
        else:
            sub.run('pkill x11vnc'.split(), 
                    stdout=sub.DEVNULL, stderr=sub.DEVNULL)

    def _start_server(self):
        address = ('', PORT)
        args = [
            'x11vnc', '-rfbport', str(PORT), '-display', 
            ':%s.0' % self._display_number,
            '-xkb', '-noxdamage', '-scale', self._scale, '-localhost',
        ]
        if self._viewonly:
            args += ['-viewonly']
        self._x11vnc_pipe = sub.Popen(
            args, stdout=sub.DEVNULL, stderr=sub.DEVNULL
        )
        if not wait_socket_listening(address, timeout=self._timeout, 
                                     tick=0.1, check_timeout=0.5):
            raise Exception('vnc not started')

    def _start_client(self):
        args = [
            'vncviewer', ':%s'%PORT, '-x11cursor', '-nocursorshape',
        ]
        if self._fullscreen:
            args += ['-fullscreen', ]
        if os.path.exists('/tmp/.X11-unix/X0'):
            sub.run(['xdotool', 'set_desktop', '1'], env={'DISPLAY':':0.0'}, check=False)
        self._vncviewer_pipe = sub.Popen(
            args, stdout=sub.DEVNULL, stderr=sub.DEVNULL, env={'DISPLAY':':0.0'}
        )
