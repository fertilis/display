# fertilis/display:1.0

FROM ubuntu:18.04

COPY var/jwm /root/jwm

RUN set -ex \
    && apt-get update \
    && echo "Installing python" \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.6 \
        python3.6-dev \
        python3-pip \
        python3-setuptools \
	locales \
    && locale-gen en_US.utf8 \
    && echo "PS1='\[\e[1;32m\]docker \[\e[1;34m\]\w\[\e[m\] '" >> /root/.bashrc \
    && echo "alias p='python'" >> /root/.bashrc\
    && echo "Installing tzdata" \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && echo "Installing jwm " \
    && apt-get install -y --no-install-recommends \
        jwm \
    && rm /etc/jwm/system.jwmrc \
    && mv /root/jwm/jwmrc.xml /root/ \
    && mv /root/jwm/jwmrc.tpl.xml /root/ \
    && ln -s /root/jwmrc.xml /root/.jwmrc \
    && rmdir /root/jwm \
    && echo "Installing xvfb " \
    && apt-get install -y --no-install-recommends \
        xvfb \
    && echo "Installing x11vnc and vncviewer " \
    && apt-get install -y --no-install-recommends \
        x11vnc \
        xtightvncviewer \
    && echo "Installing other tools " \
    && apt-get install -y --no-install-recommends \
        xsel \
        xdotool \
	x11-xserver-utils \
    && echo "Installing Pillow" \
    && apt-get install -y --no-install-recommends \
        imagemagick \
        libjpeg-dev \
        libfreetype6-dev \
    && pip3 install \
        Pillow==5.1.0 \
    && echo "Installing numpy " \
    && pip3 install \
        numpy==1.14.3 \
    && echo "Installing opencv" \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
    && pip3 install \
        opencv-python==3.3.0.9 \
    && echo "Installing imagehash" \
    && pip3 install \
        ImageHash==4.0 \
    && echo "Installing OCR tools" \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        tesseract-ocr-rus \
        tesseract-ocr-eng \
    && pip3 install \
        pyocr==0.5.1 \
    && echo "Installing GUI apps" \
    && apt-get install -y --no-install-recommends \
        leafpad \
        eom \
        gnome-screenshot \
        build-essential \
    && echo "Installing other things" \
    && pip3 install \
        ipython \
        Cython==0.28.2 \
    && mkdir -p /root/shared/fbdirs \
    && mkdir -p /root/shared/X11-unix \
    && chmod 0777 /root/shared/X11-unix \
    && rm -rf /var/lib/apt/lists/*  

ENV LANG en_US.UTF-8
ENV PATH ${PATH}:/root/app/bin

WORKDIR /root/app

COPY var /root/app/var
COPY bin /root/app/bin

COPY lib/procb /root/app/lib/procb
RUN set -ex \
    && cd /root/app/lib \
    && pip3 install -e ./procb 

COPY src /root/app/src
RUN set -ex \
    && cd /root/app \
    && pip3 install \
        -e ./src
