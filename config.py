import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPOSITORY = os.getenv('REPOSITORY', 'owner/repo')
BRANCH_PREFIX = os.getenv('BRANCH_PREFIX', 'issue2pr-')

# AI Configuration
AI_ENGINE = os.getenv('AI_ENGINE', 'gpt4')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', '#general')

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL = os.getenv('DISCORD_CHANNEL')

# Webhook Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def validate_config():
    """Validate that all required configuration is present."""
    required_vars = {
        'GITHUB_TOKEN': GITHUB_TOKEN,
        'OPENAI_API_KEY': OPENAI_API_KEY,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    if not REPOSITORY or '/' not in REPOSITORY:
        raise ValueError("REPOSITORY must be in format 'owner/repo'") 