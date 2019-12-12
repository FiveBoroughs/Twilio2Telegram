FROM python:3

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT python Twilio2Telegram.py