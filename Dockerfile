FROM python:3.12.0-alpine3.18

ENV LANG=C.UTF-8

USER root

ENV PYTHONUNBUFFERED=1

RUN mkdir -p app && touch startup.sh

ENV STARTUPDIR /app

ENV HOME /home/default

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=US/Central

WORKDIR $HOME

RUN : \
&& apk update \
&& apk --no-cache --virtual build-dependencies add g++\
&& apk --no-cache add firefox bash openblas openblas-dev \
&& :

COPY --link requirements.txt .

RUN : \
&& pip install wheel setuptools pip --upgrade \
&& pip install --no-cache-dir -r requirements.txt \
&& apk del build-dependencies py-pip \
&& rm -f /sbin/apk \
&& rm -rf /etc/apk \
&& rm -rf /lib/apk \
&& rm -rf /usr/share/apk \
&& rm -rf /var/lib/apk \
&& :

WORKDIR $STARTUPDIR

RUN : \ 
&& echo "#!/bin/bash" > $STARTUPDIR/startup.sh \
&& echo "/usr/local/bin/python3 -u /pyapp/launcher.py" >> $STARTUPDIR/startup.sh \
&& chmod +x $STARTUPDIR/startup.sh \
&& chown 1000:0 $HOME \
&& :

ENV HOME /home/user

WORKDIR $HOME

RUN mkdir -p $HOME && chown -R 1000:0 $HOME

USER 1000

ENTRYPOINT [ "/app/startup.sh" ]
