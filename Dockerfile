FROM python:3.7-alpine
WORKDIR code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY . .
