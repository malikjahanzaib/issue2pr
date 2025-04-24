from github import Github, InputGitTreeElement
from github.GithubException import GithubException
import logging
from config import GITHUB_TOKEN, REPOSITORY, BRANCH_PREFIX
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubHandler:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        logger.info("Initialized GitHub handler")

    def get_issue(self, issue_number):
        """Fetch an issue by its number."""
        try:
            return self.repo.get_issue(issue_number)
        except GithubException as e:
            logger.error(f"Error fetching issue #{issue_number}: {str(e)}")
            raise

    def create_branch(self, issue_number):
        """Create a new branch for the issue."""
        branch_name = f"{BRANCH_PREFIX}{issue_number}"
        try:
            # Get the default branch (usually main or master)
            default_branch = self.repo.default_branch
            source_branch = self.repo.get_branch(default_branch)
            
            # Create new branch
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source_branch.commit.sha
            )
            logger.info(f"Created branch {branch_name}")
            return branch_name
        except GithubException as e:
            logger.error(f"Error creating branch: {str(e)}")
            raise

    def create_pull_request(self, issue_number, branch_name, title, body):
        """Create a pull request for the issue."""
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=self.repo.default_branch
            )
            logger.info(f"Created PR #{pr.number} for issue #{issue_number}")
            return pr
        except GithubException as e:
            logger.error(f"Error creating PR: {str(e)}")
            raise

    def update_issue_status(self, issue_number, status):
        """Update the issue with a status label."""
        try:
            issue = self.get_issue(issue_number)
            issue.add_to_labels(status)
            logger.info(f"Updated issue #{issue_number} with status: {status}")
        except GithubException as e:
            logger.error(f"Error updating issue status: {str(e)}")
            raise

    def create_commit(self, branch_name, file_path, content, message):
        """Create a commit with the given content."""
        try:
            logger.info(f"Creating commit for file {file_path} on branch {branch_name}")
            logger.info(f"Content type: {type(content)}")
            logger.info(f"Content preview: {str(content)[:100]}...")
            
            # Get the current branch reference
            ref = self.repo.get_git_ref(f"heads/{branch_name}")
            
            # Get the current tree
            base_tree = self.repo.get_git_tree(sha=ref.object.sha)
            
            # Create a blob
            blob = self.repo.create_git_blob(content=content, encoding="utf-8")
            
            # Create a new tree with the updated file
            element = InputGitTreeElement(
                path=file_path,
                mode='100644',
                type='blob',
                sha=blob.sha
            )
            
            # Create a new tree with the updated file
            new_tree = self.repo.create_git_tree(
                [element],
                base_tree=base_tree
            )
            
            # Create a new commit
            parent = self.repo.get_git_commit(sha=ref.object.sha)
            commit = self.repo.create_git_commit(
                message=message,
                tree=new_tree,
                parents=[parent]
            )
            
            # Update the branch reference
            ref.edit(sha=commit.sha)
            logger.info(f"Created commit on branch {branch_name}: {message}")
        except GithubException as e:
            logger.error(f"Error creating commit: {str(e)}")
            raise

    def create_pr(self, repo_name: str, issue_number: int, title: str, body: str, changes: Dict) -> str:
        """Create a pull request with the given changes."""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)

            # Create a new branch
            branch_name = f"issue-{issue_number}"
            base_branch = repo.default_branch
            ref = repo.get_git_ref(f"heads/{base_branch}")
            repo.create_git_ref(f"refs/heads/{branch_name}", ref.object.sha)

            # Apply changes
            for file_path, content in changes.items():
                try:
                    # Try to get the file if it exists
                    try:
                        file = repo.get_contents(file_path, ref=base_branch)
                        # Update existing file
                        repo.update_file(
                            path=file_path,
                            message=f"Update {file_path} for issue #{issue_number}",
                            content=content,
                            sha=file.sha,
                            branch=branch_name
                        )
                    except:
                        # Create new file
                        repo.create_file(
                            path=file_path,
                            message=f"Create {file_path} for issue #{issue_number}",
                            content=content,
                            branch=branch_name
                        )
                except Exception as e:
                    logger.error(f"Error applying changes to {file_path}: {str(e)}")
                    raise

            # Create pull request
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base_branch
            )

            # Link PR to issue
            issue.create_comment(f"Linked PR: #{pr.number}")

            return pr.html_url

        except Exception as e:
            logger.error(f"Error creating PR: {str(e)}")
            raise

    def update_issue(self, repo_name: str, issue_number: int, comment: str) -> None:
        """Update an issue with a comment."""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            issue.create_comment(comment)
        except Exception as e:
            logger.error(f"Error updating issue: {str(e)}")
            raise

    def get_repo_info(self, repo_name: str) -> Dict:
        """Get repository information."""
        try:
            repo = self.github.get_repo(repo_name)
            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'topics': repo.get_topics(),
                'default_branch': repo.default_branch,
                'language': repo.language,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count
            }
        except Exception as e:
            logger.error(f"Error getting repo info: {str(e)}")
            raise

    def get_issue_info(self, repo_name: str, issue_number: int) -> Dict:
        """Get issue information."""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            return {
                'number': issue.number,
                'title': issue.title,
                'body': issue.body,
                'state': issue.state,
                'labels': [label.name for label in issue.labels],
                'created_at': issue.created_at.isoformat(),
                'updated_at': issue.updated_at.isoformat(),
                'comments': issue.comments
            }
        except Exception as e:
            logger.error(f"Error getting issue info: {str(e)}")
            raise

    def get_related_issues(self, repo_name: str, issue_number: int) -> list:
        """Get related issues based on labels and content."""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            related_issues = []

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

            return related_issues

        except Exception as e:
            logger.error(f"Error getting related issues: {str(e)}")
            raise 