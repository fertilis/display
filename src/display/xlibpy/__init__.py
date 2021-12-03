import os.path
import sys

sys.path.append(os.path.abspath(__file__+'/..'))

from _xlibpy import (
    init_display,
    deinit_display,
    mouse_position,
    mouse_move,
    mouse_click,
    mouse_press,
    mouse_release,
)
