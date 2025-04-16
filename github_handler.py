from github import Github
from github.GithubException import GithubException
import logging
from config import GITHUB_TOKEN, REPOSITORY, BRANCH_PREFIX

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubHandler:
    def __init__(self):
        self.github = Github(GITHUB_TOKEN)
        self.repo = self.github.get_repo(REPOSITORY)
        
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
            # Get the current branch reference
            ref = self.repo.get_git_ref(f"heads/{branch_name}")
            
            # Get the current tree
            base_tree = self.repo.get_git_tree(sha=ref.object.sha)
            
            # Create a new tree with the updated file
            new_tree = self.repo.create_git_tree(
                [{
                    'path': file_path,
                    'mode': '100644',
                    'type': 'blob',
                    'content': content
                }],
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