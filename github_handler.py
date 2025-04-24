import logging
class GitHubHandler:
def __init__(self, github_token):
self.github_token = github_token
def validate_token(self):
headers = {'Authorization': f'token {self.github_token}'}
response = requests.get('https://api.github.com/user', headers=headers)
if response.status_code == 401:
logging.error('Invalid GitHub token')
return False
return True
def make_api_call(self, endpoint):
if not self.validate_token():
return {'error': 'Invalid GitHub token'}, 401
try:
headers = {'Authorization': f'token {self.github_token}'}
response = requests.get(f'https://api.github.com/{endpoint}', headers=headers)
response.raise_for_status()
return response.json(), 200
except requests.exceptions.HTTPError as err:
logging.error(f'HTTP error occurred: {err}')
return {'error': 'An error occurred while making the API call'}, 500
except Exception as err:
logging.error(f'Error occurred: {err}')
return {'error': 'An error occurred'}, 500