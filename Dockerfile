FROM ubuntu
LABEL authors="kruase"

WORKDIR /app

RUN apt install -y python3 python3-pip python3-venv

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY . .

WORKDIR /app/resources
RUN python3 -m pip install gdown
RUN gdown 1qFR1G6t_Tdh8cKV0f3LnTWBa-EfYmMze
WORKDIR /app

CMD uvicorn main:app
