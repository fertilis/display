# Display

## Purpose

This library is intended for automation of interaction with arbitrary GUI applications. 
Suppose there is a GUI application which can only be controlled with the mouse and keyboard, and
you need to automate some work with this app. `display` module will help you.

## How to use

1. Pull the docker image

```bash
docker pull fertilis/display:1.0
```

2. Clone the repo.

```bash
git clone https://github.com/fertilis/display.git
```

3. Go to project directory

```bash
cd display
```

4. Start with running tests.

```bash
admin/tests
```

5. Try virtual displays from command line.

```bash
admin/shell python3
```

```python
>>> from display import Display
>>> d = Display(1) # instantiates virtual display :1.0
>>> d.up() # starts xvfb and jwm window manager inside it
>>> d.show() # opens vnc viewer to show you the display
``` 

Now in another terminal, open a gui app inside the docker container

```
admin/shell bash # after bash prompt appears run
DISPLAY=:1.0 leafpad
```

You will see the leafpad window in vncviewer. Suppose you want to do something with it.
Say, move the mouse cursor to some location, click, and input some text. In the terminal
with python prompt run

```python
>>> d.mouse_position()
# it will output some coordinates
>>> d.mouse_move((200, 200)) 
>>> d.mouse_position()
# now, the output should be (200, 200)
>>> d.mouse_click(button=1) # it will click left mouse button once 
>>> d.keyboard_type("Hello world!", delay=300) # delay between key strokes in ms
>>> d.down() # tears down the display
```

6. A `Display` instance can find the position of an element by matching the saved image of such element
with the image of the screen (see `Display.find_template()` method). But how to save necessary 
elements as images. `admin/devdisp` component will help.

First, create on you machine (not inside docker container) some directory and put some screenshots in it.
In the project, there is an example directory called `data` with one screenshot image inside.

```bash
admin/devdisp ./data 1366x768
```

First argument is the path to your directory with screenshots, the second argument is the screenshot resolution.
After running this command an ipython prompt will open and a vncviewer will start. Inside the vncviewer 
there will be `eom` app to display images from `./data` directory. To navigate to the next/previous image,
use arrow buttons. Once you are on the screenshot you need, go to ipython prompt and use the variable `d`
there to access the `Display` instance. In vncviewer, move the mouse to the desired location.

```python
>>> d.mouse_position()
# note the position, suppose it is (84, 36)
>>> d.pixshowtp((84, 36, 20, 30)) 
# This will open an enlarged (pixelized) image of 20x30 rectangle with top-left corner at (84, 36)
# If this fragment is not what you are looking for, change its geometry.
# Rectangle geometry is in (x, y, width, height) format.
# Now suppose, the call 
>>> d.pixshowtp((88, 40, 15, 15))
# gives you the desired element, run
>>> d.savetp((88, 40, 15, 15), 'button')
# and the file ./data/button.png will be created
# Then, if you run 
>>> d.find_template('/root/data/button.png')
# the output should be (88, 40)
# '/root/data' is the mount of ./data directory inside the container
```

7. Full `Display` API see in `display.py`

## Copyright

Egor Kalinin
