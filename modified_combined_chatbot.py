import requests
import configparser
import requests

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
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.config['CHATGPT']['ACCESS_TOKEN']
        }
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response.status_code, response.text

chatgpt = HKBU_ChatGPT()

def chat():
    user_input = request.json.get('message')
    if user_input:
        response = chatgpt.submit(user_input)
        return jsonify({"response": response})
    else:
        return jsonify({"error": "No message provided"}), 400

if __name__ == '__main__':
    port = os.getenv('PORT', '8080')  # 使用环境变量中定义的PORT，如果未定义，则默认为8080
    app.run(host='0.0.0.0', port=int(port))


from telegram.ext import Updater, MessageHandler, Filters
import configparser
import logging
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
CallbackContext)
import configparser
import logging
import redis

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


global redis1
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
    password=(config['REDIS']['PASSWORD']),
    port=(config['REDIS']['REDISPORT']))

    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    # Logging module setup
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
  # register a dispatcher to handle message: here we register an echo dispatcher
    #echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    #dispatcher.add_handler(echo_handler)
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    
   # Echo handler setup
    echo_handler = MessageHandler(Filters.text & ~Filters.command, echo)
    dispatcher.add_handler(echo_handler)
    
    # on different commands - answer in Telegram
    dispatcher.add_handler (CommandHandler("add", add))
    dispatcher.add_handler (CommandHandler("help", help_command))
    dispatcher.add_handler (CommandHandler("hello", hello))

    # Start the bot
    updater.start_polling()
    updater.idle()

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

#Send a message when the command /hello is issued. When user type /hello Kevin , it will reply Good day, Kevin!
def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Good day, ' + context.args[0] + '!')


if __name__ == '__main__':
    main()