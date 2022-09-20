FROM python:3.8-alpine
EXPOSE 8000
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ADD ./req.txt .
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev libressl-dev mariadb-dev musl-dev zlib-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
RUN python -m pip install -r req.txt
WORKDIR /app
COPY ./BAProject ./

COPY ./docker-entrypoint.sh /entry.sh
# COPY ./docker-entrypoint.sh ./
RUN ["chmod", "+x", "/entry.sh"] 
# RUN ["chmod", "+x", "/app/docker-entrypoint.sh"] 
ENTRYPOINT [ "/entry.sh" ]
# ENTRYPOINT [ "/app/docker-entrypoint.sh" ]


