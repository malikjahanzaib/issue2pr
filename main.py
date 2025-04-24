from github_handler import GitHubHandler
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def handle_webhook():
data = request.json
github_token = data.get('github_token')
handler = GitHubHandler(github_token)
result, status = handler.make_api_call('repos/user/repo')
return jsonify(result), status
if __name__ == '__main__':
app.run(debug=True)
1. In `github_handler.py`, I created a `validate_token` method which checks the token validity by making a request to a GitHub API with the token attached. If a 401 status code is returned, the token is invalid and an appropriate error message is logged. If the token is valid, the method returns True.
2. In the `make_api_call` method, I added a check for token validity. If the token is invalid, the method returns an error message and a 401 status code.
3. I wrapped the API call in a try-except block to handle any exceptions that might occur, including HTTP errors. Any exceptions are logged and a user-friendly error message is returned along with a 500 status code.
4. In `main.py`, I updated the `handle_webhook` method to use the `GitHubHandler` and its methods. The response and status from the `make_api_call` method are returned as a JSON response.