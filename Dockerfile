FROM python:3.7.2

RUN pip install -r requirements.txt

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/bot.py