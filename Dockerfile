FROM python:3.9.6-alpine3.14
COPY ./clanbotjas /clanbotjas
WORKDIR /clanbotjas
RUN apk add gcc linux-headers libc-dev
RUN pip install -r requirements.txt
RUN apk del gcc linux-headers libc-dev
CMD python ./cogmanager.py