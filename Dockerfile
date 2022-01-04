FROM alpine:3.14

WORKDIR /app
COPY requirements.txt /app/requirements.txt

# build dependencies
RUN \
    apk add --no-cache --update \
    ca-certificates \
    g++ \
    gcc \
    git \
    linux-headers \
    python3 \
    py3-pip \
    py3-pillow \
    py3-requests \
    py3-aiohttp \
    py3-beautifulsoup4 \
    py3-cryptography \
    py3-matrix-nio \
    py3-markdown \
    py3-toml \
    make && \
    pip install simplematrixbotlib -U && \
    # cleanup
    rm -rf \
    /tmp/*

COPY . /app/
CMD ["python3", "-u", "sadpandabot.py"]
