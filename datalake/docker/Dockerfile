# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

COPY ./api /root/api

WORKDIR /root

RUN pip3 install -r ./api/requirements.txt

CMD [ "python3", "-m" , "flask", "--app", "./api", "run", "--debug", "--host", "0.0.0.0", "--port", "5000"]
