FROM python:3.9.13-slim
COPY ./clanbotjas /clanbotjas
WORKDIR /clanbotjas
RUN pip install -r requirements.txt
CMD python ./cogmanager.py
