import openai
import logging
from config import OPENAI_API_KEY, AI_ENGINE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.engine = AI_ENGINE

    def generate_code(self, issue_title, issue_body, repo_context=None):
        """Generate code changes based on the issue description."""
        try:
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
            Issue Title: {issue_title}
            Issue Description: {issue_body}
            
            {f"Repository Context: {repo_context}" if repo_context else ""}
            
            Please provide the code changes needed to resolve this issue.
            Format your response as a list of file changes, where each change includes:
            1. The file path
            2. The complete new content of the file
            3. A brief explanation of the changes
            
            Example format:
            ```python
            # file: path/to/file.py
            # explanation: Added new function to handle X
            def new_function():
                # implementation
            ```
            """

            # Call GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that generates code to resolve GitHub issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error with GPT-4 generation: {str(e)}")
            raise

    def _generate_with_sweep(self, issue_title, issue_body, repo_context):
        """Generate code using Sweep.dev API."""
        # TODO: Implement Sweep.dev integration when API becomes available
        raise NotImplementedError("Sweep.dev integration is not yet implemented")

    def parse_code_changes(self, ai_response):
        """Parse the AI response into structured code changes."""
        changes = []
        current_file = None
        current_content = []
        current_explanation = None

        for line in ai_response.split('\n'):
            if line.startswith('# file:'):
                if current_file:
                    changes.append({
                        'file': current_file,
                        'content': '\n'.join(current_content),
                        'explanation': current_explanation
                    })
                current_file = line.split(': ')[1].strip()
                current_content = []
                current_explanation = None
            elif line.startswith('# explanation:'):
                current_explanation = line.split(': ')[1].strip()
            elif line and not line.startswith('#'):
                current_content.append(line)

        if current_file:
            changes.append({
                'file': current_file,
                'content': '\n'.join(current_content),
                'explanation': current_explanation
            })

        return changes 