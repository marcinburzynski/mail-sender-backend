FROM python:3.7.5

RUN mkdir /app
WORKDIR /app

ADD . /app/

ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=5000

RUN pip3 install --upgrade pip
RUN pip3 install pipenv

RUN pipenv install --skip-lock --system --dev

EXPOSE 5000

CMD gunicorn -b 0.0.0.0:$PORT -w 4 app:app
