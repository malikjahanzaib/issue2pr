import logging
from ai_engine import AIEngine
from github_handler import GitHubHandler
from config import GITHUB_TOKEN, REPOSITORY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_issue_processing(repo_name: str, issue_number: int):
    """Test the issue processing pipeline."""
    try:
        logger.info(f"Starting test for issue #{issue_number} in {repo_name}")
        
        # Initialize handlers
        ai_engine = AIEngine(GITHUB_TOKEN)
        github_handler = GitHubHandler(GITHUB_TOKEN)
        
        # Get issue information
        issue_info = github_handler.get_issue_info(repo_name, issue_number)
        logger.info(f"Issue info: {issue_info}")
        
        # Get repository information
        repo_info = github_handler.get_repo_info(repo_name)
        logger.info(f"Repository info: {repo_info}")
        
        # Get related issues
        related_issues = github_handler.get_related_issues(repo_name, issue_number)
        logger.info(f"Found {len(related_issues)} related issues")
        
        # Generate code changes
        logger.info("Generating code changes...")
        code_changes = ai_engine.generate_code(repo_name, issue_number)
        
        # Log the generated changes
        logger.info("Generated code changes:")
        logger.info(f"Explanation: {code_changes['explanation']}")
        logger.info(f"Files to modify: {code_changes['files']}")
        logger.info(f"Changes: {code_changes['changes']}")
        logger.info(f"Considerations: {code_changes['considerations']}")
        
        # Log the intended PR details
        logger.info("Test mode: Would create PR with the following details:")
        logger.info(f"Title: Fix for issue #{issue_number}")
        logger.info(f"Body: {code_changes['explanation']}")
        logger.info(f"Changes: {code_changes['changes']}")
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        raise

if __name__ == '__main__':
    # Example usage
    test_repo = "malikjahanzaib/issue2pr"  # Replace with your repository
    test_issue = 28  # Using the new issue #28
    
    test_issue_processing(test_repo, test_issue) 