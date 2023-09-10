FROM python:3.11.4
LABEL authors="kruase"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

WORKDIR /app/resources
RUN pip3 install gdown
RUN gdown 1qFR1G6t_Tdh8cKV0f3LnTWBa-EfYmMze
WORKDIR /app

CMD uvicorn main:app
