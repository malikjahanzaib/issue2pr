# Issue2PR - Automated Issue to Pull Request Bot

A GitHub bot that automatically converts issues into pull requests using AI-powered code generation.

## Features

- Automatically converts GitHub issues into pull requests
- Uses AI to generate appropriate code changes
- Supports multiple platforms (GitHub, Slack, Discord)
- Handles webhook events for real-time processing
- Includes robust error handling and logging
- Validates GitHub tokens and API responses
- Supports test mode for safe experimentation
- Includes utilities for managing issues and branches

## Setup

### Prerequisites

- Python 3.8 or higher
- GitHub account with repository access
- OpenAI API key
- ngrok (for local development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/issue2pr.git
   cd issue2pr
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```env
   GITHUB_TOKEN=your_github_token
   OPENAI_API_KEY=your_openai_api_key
   REPOSITORY=your_username/your_repo
   SLACK_TOKEN=your_slack_token  # Optional
   DISCORD_TOKEN=your_discord_token  # Optional
   ```

### Running the Application

1. Start the Python server:
   ```bash
   python main.py
   ```

2. In a separate terminal, start ngrok to expose your local server:
   ```bash
   ngrok http 5000
   ```

3. Configure GitHub webhook:
   - Go to your repository settings
   - Navigate to Webhooks
   - Add a new webhook
   - Set Payload URL to your ngrok URL (e.g., `https://your-ngrok-url.ngrok.io/webhook`)
   - Set Content type to `application/json`
   - Select "Let me select individual events" and choose:
     - Issues
     - Issue comments
   - Click "Add webhook"

### Testing

1. Run the test script to process a specific issue:
   ```bash
   python test_issue_processing.py
   ```

2. The script will:
   - Fetch the issue details
   - Generate code changes
   - Log the intended PR details
   - Not create an actual PR (test mode)

## Utilities

### Closing Issues and PRs

Use the `close_issues.py` script to close open issues and PRs:
```bash
python close_issues.py
```
This script will:
- Close all open issues
- Close all open pull requests
- Log all actions taken

### Cleaning Up Branches

Use the `delete_branches.py` script to clean up branches:
```bash
python delete_branches.py
```
This script will:
- Delete all branches except main/master
- Log all deletions
- Handle errors gracefully

## Repository Management

### File Cleanup

The repository includes a `.gitignore` file to prevent unnecessary files from being committed. Here's what's excluded:

1. **Python Files**:
   - `__pycache__/` directories
   - `*.pyc`, `*.pyo`, `*.pyd` files
   - Python build and distribution files

2. **Environment Files**:
   - `venv/` and other virtual environment directories
   - `.env` and `.env.*` files (contain sensitive information)

3. **Log Files**:
   - `*.log` files
   - `logs/` directory

4. **IDE/Editor Files**:
   - `.vscode/` and `.idea/` directories
   - `*.swp` and `*.swo` files
   - `.DS_Store` (Mac specific)

5. **Test and Coverage Files**:
   - `.coverage` and coverage reports
   - Test cache directories

### Cleaning Up

To clean up the repository manually:

```bash
# Remove all log files
rm -f *.log

# Remove Python cache directories
rm -rf __pycache__/

# Remove Mac system files
rm -f .DS_Store
```

### Best Practices

1. **Before Committing**:
   - Run the cleanup commands
   - Check for any sensitive information in files
   - Ensure all necessary files are tracked

2. **Environment Setup**:
   - Keep `.env` files local
   - Use `.env.example` for documenting required variables
   - Never commit actual credentials

3. **Logging**:
   - Log files are automatically excluded
   - Use proper logging levels
   - Check logs locally for debugging

## Usage

### Creating Issues

1. Create a new issue in your repository
2. Use a clear title describing the change needed
3. Provide detailed description of the requirements
4. The bot will automatically process the issue and create a PR

### Manual Testing

1. Use the test script to process specific issues:
   ```bash
   python test_issue_processing.py
   ```

2. Check the logs for:
   - Issue parsing
   - Code generation
   - Intended PR details

### Error Handling

The bot includes robust error handling for:
- Invalid GitHub tokens
- API rate limits
- Network errors
- Invalid webhook payloads
- Code generation failures

## Development

### Project Structure

```
issue2pr/
├── main.py              # Main application entry point
├── github_handler.py    # GitHub API interactions
├── ai_engine.py         # AI code generation
├── config.py            # Configuration settings
├── test_issue_processing.py  # Test script
├── close_issues.py      # Utility to close issues and PRs
├── delete_branches.py   # Utility to clean up branches
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Run tests:
   ```bash
   python test_issue_processing.py
   ```

4. Create a pull request

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Check ngrok is running
   - Verify webhook URL in GitHub settings
   - Check server logs for errors

2. **Invalid GitHub token**
   - Verify token has correct permissions
   - Check token format and validity
   - Look for error logs

3. **AI not generating code**
   - Verify OpenAI API key
   - Check API rate limits
   - Review issue format and content

### Logs

Logs are stored in various files:
- `app.log` - Main application logs
- `close_issues.log` - Issue/PR closing logs
- `delete_branches.log` - Branch deletion logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 