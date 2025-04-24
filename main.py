from github_handler import validate_token, process_webhook

...

@app.route('/webhook', methods=['POST'])
def handle_webhook():
"""
Endpoint to handle GitHub webhook events.
"""
payload = request.get_json()

if not validate_token(payload.get('token', '')):
return 'Invalid token', 401

if not process_webhook(payload):
return 'Failed to process webhook', 500

return '', 200

...

if __name__ == "__main__":
...
app.run(host='0.0.0.0', port=5000)