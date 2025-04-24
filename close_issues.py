#!/usr/bin/env python3
"""
Script to close open GitHub issues and pull requests, and delete their associated branches.
"""

import os
import logging
from github import Github
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('close_issues.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def delete_branch(repo, branch_name):
    """Delete a branch from the repository."""
    try:
        ref = repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()
        logger.info(f"Deleted branch: {branch_name}")
    except Exception as e:
        logger.error(f"Error deleting branch {branch_name}: {str(e)}")

def close_issues_and_prs():
    """Close all open issues and pull requests in the repository and delete their branches."""
    try:
        # Load environment variables
        load_dotenv()
        github_token = os.getenv('GITHUB_TOKEN')
        repository = os.getenv('REPOSITORY')

        if not github_token or not repository:
            logger.error("Missing required environment variables")
            return

        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(repository)

        # Get all open issues and PRs
        open_items = repo.get_issues(state='open')
        
        # Close each item and delete its branch
        for item in open_items:
            try:
                if item.pull_request:
                    # It's a PR
                    pr = repo.get_pull(item.number)
                    branch_name = pr.head.ref
                    pr.edit(state='closed')
                    logger.info(f"Closed PR #{item.number}: {item.title}")
                    # Delete the PR branch
                    delete_branch(repo, branch_name)
                else:
                    # It's an issue
                    # Check if there's a branch named after the issue
                    branch_name = f"issue-{item.number}"
                    try:
                        # Try to get the branch to see if it exists
                        repo.get_branch(branch_name)
                        # If we get here, the branch exists
                        delete_branch(repo, branch_name)
                    except:
                        # Branch doesn't exist, that's fine
                        pass
                    item.edit(state='closed')
                    logger.info(f"Closed issue #{item.number}: {item.title}")

            except Exception as e:
                logger.error(f"Error processing #{item.number}: {str(e)}")

        logger.info("Finished closing issues and PRs and deleting branches")

    except Exception as e:
        logger.error(f"Error in close_issues_and_prs: {str(e)}")

if __name__ == "__main__":
    close_issues_and_prs() 