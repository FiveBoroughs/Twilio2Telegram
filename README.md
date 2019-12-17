# ![Logo](/static/Twilio2Telegram_logo.png) Twilio2Telegram

Forward Texts and Calls from your Twilio number to Telegram

## Installation

### Clone the repository

`git clone git@github.com:FiveBoroughs/Twilio2Telegram.git && cd Twilio2Telegram`

### Set the envirronement variables

`cp sample.env .env && vim .env`

Create your bot and obtain the BotToken by following the BotFather instructions : <https://t.me/botfather>

Get the telegram owner and subscribers chat id by talking to the bot in telegram, and watching this url `https://api.telegram.org/bot<BotToken>/getUpdates`

And the Twilio Token from <https://twilio.com/console> : hidden behind the "View" button, next to auth token

### Launch the docker container

`docker-compose up -d`

### Set the Twilio webhooks destination

Click on the desired number <https://twilio.com/console/phone-numbers/incoming>

And add the domain or ip of the server hosting Twilio2Telgram, `/call` for calls and `/message` for messages

![Twilio Webhooks settings](/static/Screenshot_twilio_webhook_settings.png)

Optional :
Twilio2Telegram listens for webhook calls on the 8080 port.
If you want to add https and use the port 80, set up a reverse proxy on the machine
