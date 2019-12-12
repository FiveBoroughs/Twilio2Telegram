import os
import logging
from functools import wraps
from flask import Flask, request, abort
from waitress import serve
from twilio.request_validator import RequestValidator
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

webhook_listener = Flask(__name__)

telegram_bot = None


def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # FB - Create an instance of the RequestValidator class
        validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

        # FB - Validate the request using its URL, POST data, and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''))

        # FB - Continue processing the request if it's valid, return a 403 error if it's not
        if request_valid:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


def tg_help_handler(update):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown(
        'Find out more on [Github](https://github.com/FiveBoroughs/Twilio2Telegram)')


def tg_error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def tg_bot_start():
    """Start the telegram bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ.get('TELEGRAM_BOT_TOKEN'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", tg_help_handler))

    # log all errors
    dp.add_error_handler(tg_error_handler)

    # Start the Bot
    updater.start_polling()

    return updater.bot


def tg_send_owner_message(message):
    """Send telegram to owner."""
    telegram_bot.sendMessage(text=message, chat_id=os.environ.get(
        'TELEGRAM_OWNER'), parse_mode=ParseMode.MARKDOWN)


def tg_send_subscribers_message(message):
    """Send telegram messages."""
    for telegram_destination in os.environ.get('TELEGRAM_SUBSCRIBERS').split(','):
        telegram_bot.sendMessage(
            text=message, chat_id=telegram_destination, parse_mode=ParseMode.MARKDOWN)


@webhook_listener.route('/', methods=['GET'])
def index():
    """Return homepage."""
    return webhook_listener.send_static_file('Index.html')

# FB - Message Webhook
@webhook_listener.route('/message', methods=['POST'])
# @validate_twilio_request
def recv_message():
    """Upon reception of a SMS."""
    # FB - Format telegram Message
    telegram_message = 'Text from `+{From}` ({Country}, {State}) :```   {Body}```'.format(
        From=request.values.get('From', 'unknown'),
        Country=request.values.get('FromCountry', 'unknown'),
        State=request.values.get('FromState', 'unknown'),
        Body=request.values.get('Body', 'unknown')
    )

    # FB - Send telegram alerts
    tg_send_owner_message('Twilio ID : `{Id}`\n'.format(
        Id=request.values.get('MessageSid', 'unknown')) + telegram_message)
    tg_send_subscribers_message(telegram_message)

    # FB - return empty response to avoid further Twilio fees
    return '<response></response>'

# FB - Call Webhook
@webhook_listener.route('/call', methods=['POST'])
# @validate_twilio_request
def recv_call():
    """Upon reception of a call."""
    # FB - Format telegram Message
    telegram_message = 'Call from `+{From}` ({Country}, {State}) :```   {Status}```'.format(
        From=request.values.get('From', 'unknown'),
        Country=request.values.get('FromCountry', 'unknown'),
        State=request.values.get('FromState', 'unknown'),
        Status=request.values.get('CallStatus', 'unknown')
    )

    # FB - Send telegram alerts
    tg_send_owner_message('Twilio ID : `{Id}`\n'.format(
        Id=request.values.get('CallSid', 'unknown')) + telegram_message)
    tg_send_subscribers_message(telegram_message)

    # FB - reject the call without being billed
    return '<Response><Reject/></Response>'


if __name__ == "__main__":
    # FB - Start the telegram bot
    telegram_bot = tg_bot_start()
    # FB - Start the website
    serve(webhook_listener, host='0.0.0.0', port=8080)
