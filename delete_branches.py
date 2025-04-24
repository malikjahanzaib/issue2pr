#!/usr/bin/env python3
"""
Script to delete all branches except main/master.
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
        logging.FileHandler('delete_branches.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def delete_branches():
    """Delete all branches except main/master."""
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

        # Get all branches
        branches = repo.get_branches()
        
        # Branches to keep
        protected_branches = ['main', 'master']
        
        # Delete each branch except protected ones
        for branch in branches:
            branch_name = branch.name
            if branch_name not in protected_branches:
                try:
                    ref = repo.get_git_ref(f"heads/{branch_name}")
                    ref.delete()
                    logger.info(f"Deleted branch: {branch_name}")
                except Exception as e:
                    logger.error(f"Error deleting branch {branch_name}: {str(e)}")

        logger.info("Finished deleting branches")

    except Exception as e:
        logger.error(f"Error in delete_branches: {str(e)}")

if __name__ == "__main__":
    delete_branches() 