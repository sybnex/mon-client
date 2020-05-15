FROM alpine
LABEL maintainer="sybnex"

RUN apk --no-cache add python3 py3-psutil\
    && pip3 install --upgrade pip \
    && pip3 install pyyaml elasticsearch docker kubernetes --no-cache-dir \
    && adduser -D monitor

COPY *.py /app/
RUN chown -R monitor /app

USER monitor
