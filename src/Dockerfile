FROM python:3.8.5-alpine3.12 as base
LABEL version=${VERSION}
LABEL author='ko.ktk@pm.me'

RUN apk update
RUN apk add --no-cache python3-dev libffi-dev gcc musl-dev make

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
RUN mkdir /home/appuser/app

ADD requirements.txt /home/appuser/app
WORKDIR /home/appuser/app

RUN pip3 install -r requirements.txt
COPY . /home/appuser/app
RUN rm requirements.txt Dockerfile

ENV PATH="/home/appuser/.local/bin:${PATH}"

EXPOSE 5000 6379

CMD gunicorn --worker-class gevent --workers 1 \
--bind 0.0.0.0:5000 wsgi:app --max-requests 10000 \
--timeout 5 --keep-alive 5 --log-level debug