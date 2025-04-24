import requests
from requests.exceptions import RequestException

# Existing imports...

def is_token_valid(token: str) -> bool:
"""
Validate GitHub token format and check its validity by making a sample request to GitHub API.
"""
if not isinstance(token, str) or len(token) != 40:
return False

try:
response = requests.get('https://api.github.com/user', headers={'Authorization': f'token {token}'})
return response.status_code == 200
except RequestException:
return False

# Existing code...

class GitHubHandler:

# Existing code...

def make_api_call(self, url: str, method: str, data=None):
if not is_token_valid(self.token):
logging.error('Invalid GitHub token')
return None, 401

# Existing try-catch block...
