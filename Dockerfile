FROM python:3.7.5-slim-buster

ENV PYTHONUNBUFFERED=true

ARG user=hotel_api
ARG group=hotel_api
ARG uid=1000
ARG gid=1000

RUN groupadd -g ${gid} ${group} \
  && useradd -u ${uid} -g ${group} -s /bin/sh ${user}

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

ENV INSTALL_PATH /hotel_api
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .

USER ${user}

CMD gunicorn -b 0.0.0.0:$PORT --access-logfile - "hotel_api.app:create_app()"