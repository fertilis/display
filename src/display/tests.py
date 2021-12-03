import subprocess as sub
import unittest
import time
import os

from .display import Display
from .wait import wait_process_ended


def path(name):
    return '/root/app/repo/display/var/{}.png'.format(name)


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Display(1)
        cls.d.up()
        if os.environ.get('DISPLAY') == ':0.0':
            cls.d.show()

    @classmethod
    def tearDownClass(cls):
        cls.d.down()

    def test_main(self):
        print('\nRunning main test')
        sub.Popen(['leafpad'], env={'DISPLAY':':1.0'}, stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        cross_path = path('cross')
        print('asserting cross')
        self.d.assert_find_template((cross_path,), 5, 1)
        print('cross asserted')
        pt = self.d.find_template(cross_path)
        print('cross found at: {}'.format(pt))
        print('checking match')
        self.d.assert_match_template((cross_path, pt), 5, 1)
        print('match checked')

        print('printing text')
        self.d.click_point((330, 330))
        time.sleep(0.5)
        self.d.keyboard_type('hi fellows')
        print('printing text done')

        w, h = self.d.get_template_size(cross_path)
        print('cross template size: {}'.format((w,h)))
        print('clicking cross until no button appears')
        rect = pt[0], pt[1], w, h
        nobtn_path = path('no_btn')
        self.d.click_change(
            rect, (nobtn_path,), timeout=5, tick=0.1, method='wait_find_template' 
        )
        print('cross clicked')
        pt = self.d.find_template(nobtn_path)
        print('nobtn found at: {}'.format(pt))
        self.d.assert_match_template((nobtn_path, pt), 5, 1)
        print('match checked')
        print('clicking nobtn rect')
        w, h = self.d.get_template_size(nobtn_path)
        rect = pt[0], pt[1], w, h
        self.d.click_rect(rect)
        print('waiting leafpad to end')
        wait_process_ended('leafpad', 5, 1, 1)
