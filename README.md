# Issue2PR Bot

A GitHub bot that automatically converts issues into Pull Requests using AI-powered code generation.

## Features

- Monitors GitHub repositories for new or labeled issues
- Uses GPT-4 or Sweep.dev to generate code changes
- Creates Pull Requests automatically
- Optional Slack/Discord integration for notifications
- Configurable AI engine selection

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/issue2pr.git
cd issue2pr
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials:
```env
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
SLACK_BOT_TOKEN=your_slack_bot_token  # Optional
DISCORD_BOT_TOKEN=your_discord_bot_token  # Optional
```

4. Set up GitHub webhook:
   - Go to your repository settings
   - Add a webhook with the following settings:
     - Payload URL: `https://your-domain.com/webhook`
     - Content type: `application/json`
     - Events: Select "Issues" and "Issue comments"

5. Run the bot:
```bash
python main.py
```

## Configuration

The bot can be configured through environment variables:

- `AI_ENGINE`: Choose between "gpt4" or "sweep" (default: "gpt4")
- `REPOSITORY`: Target GitHub repository (format: owner/repo)
- `BRANCH_PREFIX`: Prefix for generated branches (default: "issue2pr-")

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License 