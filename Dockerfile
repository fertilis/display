# displaydev:latest

FROM dev.ru:90/display:1.0.0

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        leafpad \
        eom \
        gnome-screenshot \
        build-essential \
    && pip install \
        ipython \
        Cython==0.28.2 
#    && rm -rf /var/lib/apt/lists/* 

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        tesseract-ocr-rus \
        tesseract-ocr-eng \
    && pip install \
        pyocr==0.5.1 

ENV PATH ${PATH}:/root/app/repo/display/bin
COPY src /root/app/repo/display/src
COPY var /root/app/repo/display/var
RUN cd /root/app/repo/display \
    && pip install \
        -e ./src 
COPY bin /root/app/repo/display/bin

COPY lib/procb /root/app/repo/display/lib/procb
RUN cd /root/app/repo/display/lib \
    && pip install -e ./procb

WORKDIR /root/app

