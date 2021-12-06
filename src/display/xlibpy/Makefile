
all: ./xlibpy.c 
	apt-get update && apt-get install libx11-dev && \
	gcc -shared -o ./_xlibpy.so -fPIC ./xlibpy.c -I/usr/include/python3.6m -lX11
