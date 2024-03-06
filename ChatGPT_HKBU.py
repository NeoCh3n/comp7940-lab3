from flask import Flask, request, jsonify
import configparser
import requests
import os

app = Flask(__name__)

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

@app.route('/chat', methods=['POST'])
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
