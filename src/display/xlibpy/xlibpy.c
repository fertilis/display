#include <Python.h>
#include <X11/Xlib.h>
#include <unistd.h>


static Display *display;

static PyObject *
init_display(PyObject *self, PyObject *args) {
    unsigned int display_number;
    char display_name[20]; 
    if (!PyArg_ParseTuple(args, "I", &display_number)) {
	return NULL;
    }
    snprintf(display_name, 20, ":%d.0", display_number);
    if (display) {
	char error_message[100];
	snprintf(error_message, 100, "Cannot initialize display: first with deinit_display()");
	PyErr_SetString(PyExc_RuntimeError, error_message);
	return NULL;
    }
    display = XOpenDisplay(display_name);
    if (!display) {
	char error_message[100];
	snprintf(error_message, 100, "Cannot initialize display %d", display_number);
	PyErr_SetString(PyExc_RuntimeError, error_message);
	return NULL;
    }
    XSetCloseDownMode(display, DestroyAll);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
deinit_display() {
    display = 0;
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
mouse_move(PyObject *self, PyObject *args) {
    unsigned short tgt_x, tgt_y;
    unsigned int delay;
    int cur_x = -1;
    int cur_y = -1;
    Window temp_win;
    int temp_int;
    unsigned int temp_uint;

    if (!display) {
	PyErr_SetString(PyExc_RuntimeError, "initialize display with init_display(num)");
	return NULL;
    }

    int foo_x, foo_y;
    if (!PyArg_ParseTuple(args, "HHI", &tgt_x, &tgt_y, &delay)) {
	return NULL;
    }
    int screen = XDefaultScreen(display);
    Window root_window = XRootWindow(display, screen);

    int screen_width = DisplayWidth(display, screen);
    int screen_height = DisplayHeight(display, screen);

    if (tgt_x > screen_width) {
	tgt_x = screen_width;
    }
    if (tgt_x < 0) {
	tgt_x = 0;
    }
    if (tgt_y > screen_height) {
	tgt_y = screen_height;
    }
    if (tgt_y < 0) {
	tgt_y = 0;
    }

    XQueryPointer(display, root_window, &temp_win, &temp_win, &temp_int, &temp_int, &cur_x, &cur_y, &temp_uint);

    if (cur_x == -1 || cur_y == -1 || !delay) {
	XWarpPointer(display, None, root_window, 0, 0, 0, 0, tgt_x, tgt_y);
	XFlush(display);
	Py_INCREF(Py_None);
	return Py_None;
    }

    int dx =  abs (tgt_x - cur_x), sx = cur_x < tgt_x ? 1 : -1;
    int dy = -abs (tgt_y - cur_y), sy = cur_y < tgt_y ? 1 : -1; 
    int err = dx + dy, e2; /* error value e_xy */

    for (;;){  /* loop */
	XWarpPointer(display, None, root_window, 0, 0, 0, 0, cur_x, cur_y);
	XFlush(display);
	if (cur_x == tgt_x && cur_y == tgt_y) break;
	usleep(delay);
	e2 = 2 * err;
	if (e2 >= dy) { err += dy; cur_x += sx; } /* e_xy+e_x > 0 */
	if (e2 <= dx) { err += dx; cur_y += sy; } /* e_xy+e_y < 0 */
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
mouse_position() {
    int x = -1;
    int y = -1;
    Window temp_win;
    int temp_int;
    unsigned int temp_uint;

    if (!display) {
	PyErr_SetString(PyExc_RuntimeError, "initialize display with init_display(num)");
	return NULL;
    }

    int screen = XDefaultScreen(display);
    Window root_window = XRootWindow(display, screen);

    XQueryPointer(display, root_window, &temp_win, &temp_win, &temp_int, &temp_int, &x, &y, &temp_uint);
    
    PyObject *ret = Py_BuildValue("ii", x, y);
    return ret;
}

static PyObject *
mouse_click (PyObject *self, PyObject *args) {
    if (!display) {
	PyErr_SetString(PyExc_RuntimeError, "initialize display with init_display(num)");
	return NULL;
    }

    int button, delay;
    if (!PyArg_ParseTuple(args, "ii", &button, &delay)) {
	return NULL;
    }

    // Create and setting up the event
    XEvent event;
    memset (&event, 0, sizeof (event));
    event.xbutton.button = button;
    event.xbutton.same_screen = True;
    event.xbutton.subwindow = DefaultRootWindow (display);
    while (event.xbutton.subwindow) {
        event.xbutton.window = event.xbutton.subwindow;
        XQueryPointer (
            display, event.xbutton.window,
            &event.xbutton.root, &event.xbutton.subwindow,
            &event.xbutton.x_root, &event.xbutton.y_root,
            &event.xbutton.x, &event.xbutton.y,
            &event.xbutton.state
        );
    }
    // Press
    event.type = ButtonPress;
    if (XSendEvent (display, PointerWindow, True, ButtonPressMask, &event) == 0) {
        fprintf (stderr, "Error to send the event!\n");
    }
    XFlush (display);
    usleep (delay);
    // Release
    event.type = ButtonRelease;
    if (XSendEvent (display, PointerWindow, True, ButtonReleaseMask, &event) == 0) { 
        fprintf (stderr, "Error to send the event!\n");
    }
    XFlush (display);
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
mouse_press (PyObject *self, PyObject *args) {
    if (!display) {
	PyErr_SetString(PyExc_RuntimeError, "initialize display with init_display(num)");
	return NULL;
    }

    int button;
    if (!PyArg_ParseTuple(args, "i", &button)) {
	return NULL;
    }

    // Create and setting up the event
    XEvent event;
    memset (&event, 0, sizeof (event));
    event.xbutton.button = button;
    event.xbutton.same_screen = True;
    event.xbutton.subwindow = DefaultRootWindow (display);
    while (event.xbutton.subwindow) {
        event.xbutton.window = event.xbutton.subwindow;
        XQueryPointer (
            display, event.xbutton.window,
            &event.xbutton.root, &event.xbutton.subwindow,
            &event.xbutton.x_root, &event.xbutton.y_root,
            &event.xbutton.x, &event.xbutton.y,
            &event.xbutton.state
        );
    }
    // Press
    event.type = ButtonPress;
    if (XSendEvent (display, PointerWindow, True, ButtonPressMask, &event) == 0) {
        fprintf (stderr, "Error to send the event!\n");
    }
    XFlush (display);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
mouse_release (PyObject *self, PyObject *args) {
    if (!display) {
	PyErr_SetString(PyExc_RuntimeError, "initialize display with init_display(num)");
	return NULL;
    }

    int button;
    if (!PyArg_ParseTuple(args, "i", &button)) {
	return NULL;
    }

    // Create and setting up the event
    XEvent event;
    memset (&event, 0, sizeof (event));
    event.xbutton.button = button;
    event.xbutton.same_screen = True;
    event.xbutton.subwindow = DefaultRootWindow (display);
    while (event.xbutton.subwindow) {
        event.xbutton.window = event.xbutton.subwindow;
        XQueryPointer (
            display, event.xbutton.window,
            &event.xbutton.root, &event.xbutton.subwindow,
            &event.xbutton.x_root, &event.xbutton.y_root,
            &event.xbutton.x, &event.xbutton.y,
            &event.xbutton.state
        );
    }
    // Release
    event.type = ButtonRelease;
    if (XSendEvent (display, PointerWindow, True, ButtonReleaseMask, &event) == 0) { 
        fprintf (stderr, "Error to send the event!\n");
    }
    XFlush (display);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef Methods[] = {
    {"mouse_move", mouse_move, METH_VARARGS, "moves mouse"},
    {"mouse_click", mouse_click, METH_VARARGS, "presses and releases mouse buttons"},
    {"mouse_press", mouse_press, METH_VARARGS, "presses mouse buttons"},
    {"mouse_release", mouse_release, METH_VARARGS, "releases mouse buttons"},
    {"mouse_position", mouse_position, METH_NOARGS, "returns mouse position"},
    {"init_display", init_display, METH_VARARGS, "initializes display"},
    {"deinit_display", deinit_display, METH_NOARGS, "deinitializes display"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "xlibpy",
    "xlib wrapper",
    -1,
    Methods
};


PyMODINIT_FUNC
PyInit__xlibpy(void) {
    XInitThreads();
    return PyModule_Create(&module);
}

