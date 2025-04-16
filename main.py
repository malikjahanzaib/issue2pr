import os
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify
from github_handler import GitHubHandler
from ai_engine import AIEngine
from config import WEBHOOK_SECRET, validate_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize handlers
github_handler = GitHubHandler()
ai_engine = AIEngine()

# Track processed issues to prevent duplicates
processed_issues = set()

app = Flask(__name__)

def verify_webhook_signature(payload, signature):
    """Verify the GitHub webhook signature."""
    if not WEBHOOK_SECRET:
        logger.warning("No webhook secret configured, skipping signature verification")
        return True
    
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected_signature}",
        signature
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events."""
    try:
        # Verify the request is from GitHub
        signature = request.headers.get('X-Hub-Signature-256')
        if not verify_webhook_signature(request.data, signature):
            return 'Invalid signature', 403

        # Parse the webhook payload
        payload = request.json
        event = request.headers.get('X-GitHub-Event')
        
        # Only process issue events
        if event != 'issues':
            return 'Ignoring non-issue event', 200
            
        # Only process opened or labeled issues
        action = payload.get('action')
        if action not in ['opened', 'labeled']:
            return 'Ignoring non-opened/labeled issue', 200
            
        # Get issue details
        issue = payload.get('issue', {})
        issue_number = issue.get('number')
        title = issue.get('title')
        body = issue.get('body')
        labels = [label['name'] for label in issue.get('labels', [])]
        
        # Check if issue has already been processed
        if issue_number in processed_issues:
            logger.info(f"Issue #{issue_number} has already been processed")
            return 'Issue already processed', 200
            
        # Check if issue has the 'bot:ignore' label
        if 'bot:ignore' in labels:
            logger.info(f"Ignoring issue #{issue_number} due to bot:ignore label")
            return 'Issue ignored due to label', 200
            
        # Check if issue has the 'bot:urgent' label
        is_urgent = 'bot:urgent' in labels
        
        # Process the issue
        process_issue(issue_number, title, body, is_urgent)
        
        # Mark issue as processed
        processed_issues.add(issue_number)
        
        return 'Webhook processed successfully', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return 'Error processing webhook', 500

def handle_issue_event(payload):
    """Handle GitHub issue events."""
    action = payload.get('action')
    issue = payload.get('issue')
    
    if not issue:
        return
    
    issue_number = issue.get('number')
    issue_title = issue.get('title')
    issue_body = issue.get('body')
    
    if action in ['opened', 'labeled']:
        logger.info(f"Processing issue #{issue_number}: {issue_title}")
        process_issue(issue_number, issue_title, issue_body)

def handle_issue_comment(payload):
    """Handle GitHub issue comment events."""
    comment = payload.get('comment')
    issue = payload.get('issue')
    
    if not comment or not issue:
        return
    
    # Check if the comment contains a trigger command
    if '/issue2pr' in comment.get('body', '').lower():
        issue_number = issue.get('number')
        issue_title = issue.get('title')
        issue_body = issue.get('body')
        
        logger.info(f"Processing issue #{issue_number} via comment trigger")
        process_issue(issue_number, issue_title, issue_body)

def process_issue(issue_number, title, body, is_urgent=False):
    """Process an issue and create a PR with AI-generated changes."""
    try:
        logger.info(f"Processing issue #{issue_number}: {title}")
        if is_urgent:
            logger.info("Processing urgent issue")
        
        # Generate code changes using AI
        ai_response = ai_engine.generate_code(title, body)
        code_changes = ai_engine.parse_code_changes(ai_response)
        
        if not code_changes:
            logger.warning(f"No code changes generated for issue #{issue_number}")
            return
        
        logger.info(f"Generated {len(code_changes)} code changes")
        
        # Create a new branch
        branch_name = github_handler.create_branch(issue_number)
        logger.info(f"Created branch {branch_name}")
        
        # Apply code changes
        for change in code_changes:
            try:
                logger.info(f"Creating file {change['file']}")
                # Clean up the content
                content = change['content'].strip()
                if content.startswith('```'):
                    content = content.split('```')[1].strip()
                if content.endswith('```'):
                    content = content.rsplit('```', 1)[0].strip()
                
                # Log the content for debugging
                logger.info(f"Content type: {type(content)}")
                logger.info(f"Content preview: {content[:100]}...")
                
                github_handler.create_commit(
                    branch_name=branch_name,
                    file_path=change['file'],
                    content=content,
                    message=f"Update {change['file']}: {change['explanation']}"
                )
            except Exception as e:
                logger.error(f"Error creating file {change['file']}: {str(e)}")
                raise
        
        # Create pull request
        pr_title = f"Resolve #{issue_number}: {title}"
        pr_body = f"""This PR resolves issue #{issue_number}

Changes made:
{chr(10).join(f"- {change['file']}: {change['explanation']}" for change in code_changes)}

Generated by Issue2PR Bot using {ai_engine.engine.upper()}
"""
        
        pr = github_handler.create_pull_request(
            issue_number=issue_number,
            branch_name=branch_name,
            title=pr_title,
            body=pr_body
        )
        
        # Update issue status
        status = "PR Created ✅ (Urgent)" if is_urgent else "PR Created ✅"
        github_handler.update_issue_status(issue_number, status)
        
        logger.info(f"Successfully created PR #{pr.number} for issue #{issue_number}")
        
    except Exception as e:
        logger.error(f"Error processing issue #{issue_number}: {str(e)}")
        raise

if __name__ == '__main__':
    # Validate configuration
    validate_config()
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=3000) 