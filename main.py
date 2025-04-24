import os
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify
from github_handler import GitHubHandler
from ai_engine import AIEngine
from config import WEBHOOK_SECRET, validate_config, GITHUB_TOKEN, AI_ENGINE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize handlers
github_handler = GitHubHandler(GITHUB_TOKEN)
ai_engine = AIEngine(GITHUB_TOKEN)

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
def handle_webhook():
    try:
        # Verify webhook signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature or not verify_webhook_signature(request.data, signature):
            return jsonify({'error': 'Invalid signature'}), 401

        # Parse webhook payload
        payload = request.json
        event_type = request.headers.get('X-GitHub-Event')

        if event_type == 'issues':
            handle_issue_event(payload)
        elif event_type == 'issue_comment':
            handle_issue_comment(payload)
        else:
            logger.info(f"Ignoring unsupported event type: {event_type}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def handle_issue_event(payload):
    """Handle GitHub issue events."""
    action = payload.get('action')
    issue = payload.get('issue')
    repository = payload.get('repository')

    if not all([action, issue, repository]):
        logger.error("Missing required fields in issue event payload")
        return

    repo_name = repository['full_name']
    issue_number = issue['number']

    if action in ['opened', 'labeled']:
        logger.info(f"Processing issue #{issue_number} in {repo_name}")
        
        try:
            # Generate code changes using AI
            code_changes = ai_engine.generate_code(repo_name, issue_number)
            
            # Create PR with the changes
            pr_url = github_handler.create_pr(
                repo_name=repo_name,
                issue_number=issue_number,
                title=f"Fix for issue #{issue_number}",
                body=code_changes['explanation'],
                changes=code_changes['changes']
            )
            
            logger.info(f"Created PR: {pr_url}")
            
            # Update issue with PR link
            github_handler.update_issue(
                repo_name=repo_name,
                issue_number=issue_number,
                comment=f"PR created: {pr_url}"
            )

        except Exception as e:
            logger.error(f"Error processing issue: {str(e)}")
            github_handler.update_issue(
                repo_name=repo_name,
                issue_number=issue_number,
                comment=f"Error processing issue: {str(e)}"
            )

def handle_issue_comment(payload):
    """Handle GitHub issue comment events."""
    action = payload.get('action')
    comment = payload.get('comment')
    issue = payload.get('issue')
    repository = payload.get('repository')

    if not all([action, comment, issue, repository]):
        logger.error("Missing required fields in comment event payload")
        return

    if action == 'created' and comment['body'].startswith('/generate'):
        repo_name = repository['full_name']
        issue_number = issue['number']
        
        try:
            # Generate code changes using AI
            code_changes = ai_engine.generate_code(repo_name, issue_number)
            
            # Create PR with the changes
            pr_url = github_handler.create_pr(
                repo_name=repo_name,
                issue_number=issue_number,
                title=f"Fix for issue #{issue_number}",
                body=code_changes['explanation'],
                changes=code_changes['changes']
            )
            
            logger.info(f"Created PR: {pr_url}")
            
            # Update issue with PR link
            github_handler.update_issue(
                repo_name=repo_name,
                issue_number=issue_number,
                comment=f"PR created: {pr_url}"
            )

        except Exception as e:
            logger.error(f"Error processing comment: {str(e)}")
            github_handler.update_issue(
                repo_name=repo_name,
                issue_number=issue_number,
                comment=f"Error processing comment: {str(e)}"
            )

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
    app.run(host='0.0.0.0', port=3000, debug=True) 