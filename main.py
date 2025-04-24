from flask import Flask, request, jsonify
from github_handler import GitHubHandler, is_token_valid

# Existing imports...

app = Flask(__name__)
github_handler = GitHubHandler()

@app.route('/webhook', methods=['POST'])
def process_webhook():
if not request.is_json:
return jsonify({'message': 'Invalid payload'}), 400

data = request.get_json()
token = data.get('token')

if not is_token_valid(token):
return jsonify({'message': 'Invalid GitHub token'}), 401

# Existing processing logic...

return jsonify({'message': 'Webhook processed'}), 200

# Existing code...