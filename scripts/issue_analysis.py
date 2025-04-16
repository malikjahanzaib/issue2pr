import requests
from datetime import datetime
from collections import Counter
GITHUB_TOKEN = 'your_github_token'
REPO_OWNER = 'your_username'
REPO_NAME = 'your_repo_name'
API_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
headers = {
'Authorization': f'token {GITHUB_TOKEN}',
'Accept': 'application/vnd.github.v3+json'
}
def get_issues():
response = requests.get(API_URL, headers=headers)
return response.json()
def analyze_issues():
issues = get_issues()
label_counts = Counter()
resolve_times = []
for issue in issues:
for label in issue['labels']:
label_counts[label['name']] += 1
if issue['closed_at']:
open_time = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
close_time = datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
resolve_times.append((close_time - open_time).days)
avg_resolve_time = sum(resolve_times) / len(resolve_times) if resolve_times else 0
return label_counts, avg_resolve_time
def generate_report():
label_counts, avg_resolve_time = analyze_issues()
report = {
'label_counts': label_counts,
'average_resolve_time': avg_resolve_time
}
print('Report:')
print('Label Counts:', dict(label_counts))
print('Average Resolve Time:', avg_resolve_time)
with open('report.json', 'w') as f:
json.dump(report, f)
if __name__ == "__main__":
generate_report()