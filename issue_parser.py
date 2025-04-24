import logging
from typing import Dict, List, Optional
from github import Github
from github.Repository import Repository
from github.Issue import Issue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IssueParser:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.context_cache = {}

    def parse_issue(self, repo_name: str, issue_number: int) -> Dict:
        """Parse an issue and gather relevant context."""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            
            # Gather basic issue information
            issue_info = {
                'title': issue.title,
                'body': issue.body,
                'labels': [label.name for label in issue.labels],
                'state': issue.state,
                'created_at': issue.created_at.isoformat(),
                'updated_at': issue.updated_at.isoformat(),
            }

            # Gather additional context
            context = {
                'related_issues': self._get_related_issues(repo, issue),
                'repository_info': self._get_repository_info(repo),
                'code_context': self._get_code_context(repo, issue),
                'documentation': self._get_relevant_documentation(repo, issue),
            }

            return {
                'issue': issue_info,
                'context': context
            }

        except Exception as e:
            logger.error(f"Error parsing issue: {str(e)}")
            raise

    def _get_related_issues(self, repo: Repository, issue: Issue) -> List[Dict]:
        """Get related issues based on labels and content similarity."""
        related_issues = []
        try:
            # Get issues with similar labels
            for label in issue.labels:
                for related_issue in repo.get_issues(state='all', labels=[label.name]):
                    if related_issue.number != issue.number:
                        related_issues.append({
                            'number': related_issue.number,
                            'title': related_issue.title,
                            'state': related_issue.state,
                            'url': related_issue.html_url
                        })
        except Exception as e:
            logger.error(f"Error getting related issues: {str(e)}")
        return related_issues

    def _get_repository_info(self, repo: Repository) -> Dict:
        """Get relevant repository information."""
        try:
            return {
                'description': repo.description,
                'topics': repo.get_topics(),
                'default_branch': repo.default_branch,
                'contributors': [contributor.login for contributor in repo.get_contributors()],
                'recent_commits': self._get_recent_commits(repo)
            }
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return {}

    def _get_recent_commits(self, repo: Repository, limit: int = 5) -> List[Dict]:
        """Get recent commits from the repository."""
        commits = []
        try:
            for commit in repo.get_commits()[:limit]:
                commits.append({
                    'sha': commit.sha,
                    'message': commit.commit.message,
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date.isoformat()
                })
        except Exception as e:
            logger.error(f"Error getting recent commits: {str(e)}")
        return commits

    def _get_code_context(self, repo: Repository, issue: Issue) -> Dict:
        """Get relevant code context based on issue content."""
        code_context = {}
        try:
            # Search for code references in issue body
            import re
            code_refs = re.findall(r'`([^`]+)`', issue.body)
            
            for ref in code_refs:
                try:
                    # Try to find the file and line number
                    content = repo.get_contents(ref)
                    if content:
                        code_context[ref] = {
                            'content': content.decoded_content.decode(),
                            'path': content.path
                        }
                except:
                    continue
        except Exception as e:
            logger.error(f"Error getting code context: {str(e)}")
        return code_context

    def _get_relevant_documentation(self, repo: Repository, issue: Issue) -> Dict:
        """Get relevant documentation based on issue content."""
        docs = {}
        try:
            # Look for documentation files
            doc_files = ['README.md', 'CONTRIBUTING.md', 'docs/']
            for doc_file in doc_files:
                try:
                    content = repo.get_contents(doc_file)
                    if content:
                        docs[doc_file] = content.decoded_content.decode()
                except:
                    continue
        except Exception as e:
            logger.error(f"Error getting documentation: {str(e)}")
        return docs 