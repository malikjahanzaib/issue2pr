import openai
import logging
from config import OPENAI_API_KEY, AI_ENGINE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.engine = AI_ENGINE
        logger.info(f"Initialized AI Engine with {self.engine}")

    def generate_code(self, issue_title, issue_body, repo_context=None):
        """Generate code changes based on the issue description."""
        try:
            logger.info(f"Generating code for issue: {issue_title}")
            if self.engine == "gpt4":
                return self._generate_with_gpt4(issue_title, issue_body, repo_context)
            elif self.engine == "sweep":
                return self._generate_with_sweep(issue_title, issue_body, repo_context)
            else:
                raise ValueError(f"Unsupported AI engine: {self.engine}")
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise

    def _generate_with_gpt4(self, issue_title, issue_body, repo_context):
        """Generate code using GPT-4."""
        try:
            # Prepare the prompt
            prompt = f"""
            You are an expert Python developer. Your task is to help resolve a GitHub issue by generating the necessary code changes.

            Issue Title: {issue_title}
            Issue Description: {issue_body}
            
            {f"Repository Context: {repo_context}" if repo_context else ""}
            
            Please provide the code changes needed to resolve this issue. For each file that needs to be created or modified:
            1. Specify the file path
            2. Provide the complete new content of the file
            3. Include a brief explanation of the changes
            
            Format your response exactly like this example:
            ```python
            # file: README.md
            # explanation: Added comprehensive project documentation
            # Issue2PR Bot
            # A GitHub bot that automatically converts issues into Pull Requests using AI-powered code generation.

            ## Overview
            Issue2PR Bot is an automated solution that transforms GitHub issues into Pull Requests using AI. It monitors repositories for new issues, generates appropriate code changes using GPT-4, and creates PRs automatically.

            ## Features
            - 🚀 **Automatic PR Generation**: Converts issues to PRs with AI-generated code
            - 🤖 **AI-Powered**: Uses GPT-4 for intelligent code generation
            - 🔄 **Real-time Monitoring**: Watches for new issues and labels
            - 📊 **Status Updates**: Updates issue status with PR progress
            - 🔒 **Secure**: Verifies webhook signatures and handles errors gracefully

            ## Setup
            1. **Clone the Repository**
               ```bash
               git clone https://github.com/yourusername/issue2pr.git
               cd issue2pr
               ```

            2. **Install Dependencies**
               ```bash
               pip install -r requirements.txt
               ```

            3. **Configure Environment Variables**
               Create a `.env` file with:
               ```
               GITHUB_TOKEN=your_github_token
               OPENAI_API_KEY=your_openai_key
               WEBHOOK_SECRET=your_webhook_secret
               ```

            4. **Run the Bot**
               ```bash
               python main.py
               ```

            ## Configuration
            - `GITHUB_TOKEN`: Your GitHub personal access token
            - `OPENAI_API_KEY`: Your OpenAI API key
            - `WEBHOOK_SECRET`: Secret for webhook verification
            - `REPOSITORY`: Target repository (format: owner/repo)
            - `BRANCH_PREFIX`: Prefix for created branches
            - `AI_ENGINE`: AI engine to use (gpt4 or sweep)

            ## Usage
            1. Create an issue in your repository
            2. The bot will automatically:
               - Generate appropriate code changes
               - Create a new branch
               - Create a PR with the changes
               - Update the issue status

            ## Contributing
            Contributions are welcome! Please feel free to submit a Pull Request.

            ## License
            This project is licensed under the MIT License - see the LICENSE file for details.
            ```

            Important:
            - For README files, use proper Markdown formatting
            - For Python files, include all necessary imports and code
            - Make sure the content is complete and properly formatted
            - Include all necessary sections and information
            """

            logger.info("Sending request to GPT-4")
            # Call GPT-4 using the new API format
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that generates code to resolve GitHub issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            logger.info(f"Received response from GPT-4: {content[:200]}...")  # Log first 200 chars
            
            if not content.strip():
                logger.error("Empty response received from GPT-4")
                raise ValueError("Empty response from GPT-4")
                
            return content
        except Exception as e:
            logger.error(f"Error with GPT-4 generation: {str(e)}")
            raise

    def _generate_with_sweep(self, issue_title, issue_body, repo_context):
        """Generate code using Sweep.dev API."""
        # TODO: Implement Sweep.dev integration when API becomes available
        raise NotImplementedError("Sweep.dev integration is not yet implemented")

    def parse_code_changes(self, ai_response):
        """Parse the AI response into structured code changes."""
        logger.info("Parsing code changes from AI response")
        changes = []
        current_file = None
        current_content = []
        current_explanation = None
        in_code_block = False
        skip_next_line = False

        for line in ai_response.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('# file:'):
                if current_file and current_content:
                    content = '\n'.join(current_content).strip()
                    if content:
                        changes.append({
                            'file': current_file,
                            'content': content,
                            'explanation': current_explanation or 'No explanation provided'
                        })
                current_file = line.split(':', 1)[1].strip()
                current_content = []
                current_explanation = None
                in_code_block = False
            elif line.startswith('# explanation:'):
                current_explanation = line.split(':', 1)[1].strip()
            elif line.startswith('```'):
                if not in_code_block:
                    skip_next_line = True  # Skip language identifier line
                in_code_block = not in_code_block
            elif not skip_next_line and (in_code_block or not line.startswith('#')):
                current_content.append(line)
            else:
                skip_next_line = False

        # Don't forget the last file
        if current_file and current_content:
            content = '\n'.join(current_content).strip()
            if content:
                changes.append({
                    'file': current_file,
                    'content': content,
                    'explanation': current_explanation or 'No explanation provided'
                })

        logger.info(f"Parsed {len(changes)} code changes")
        for change in changes:
            logger.info(f"File: {change['file']}")
            logger.info(f"Content preview: {change['content'][:100]}...")
            logger.info(f"Explanation: {change['explanation']}")

        return changes 