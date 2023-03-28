ARG PORT=443

FROM cypress/browsers:latest
FROM python:3.10

COPY requirements.txt  .

ENV PATH /home/root/.local/bin:${PATH}

RUN  apt-get update && apt-get install -y python3-pip && pip install -U -r requirements.txt  

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
