import configparser
import logging
import redis
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Define command handlers
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

# Handler that uses the HKBU_ChatGPT class
def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Main function
def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    global redis1, chatgpt
    redis1 = redis.Redis(host=config['REDIS']['HOST'], password=config['REDIS']['PASSWORD'], port=config['REDIS']['REDISPORT'])
    chatgpt = HKBU_ChatGPT(config)

    updater = Updater(token=config['TELEGRAM']['ACCESS_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add))

    updater.start_polling()
    updater.idle()

# HKBU_ChatGPT class definition
class HKBU_ChatGPT:
    def __init__(self, config_path='./config.ini'):
        if isinstance(config_path, str):
            self.config = configparser.ConfigParser()
            self.config.read(config_path)
        elif isinstance(config_path, configparser.ConfigParser):
            self.config = config_path

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = self.config['CHATGPT']['BASICURL'] + "/deployments/" + self.config['CHATGPT']['MODELNAME'] + "/chat/completions/?api-version=" + self.config['CHATGPT']['APIVERSION']
        headers = {'Content-Type': 'application/json', 'api-key': self.config['CHATGPT']['ACCESS_TOKEN']}
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response

if __name__ == '__main__':
    main()
