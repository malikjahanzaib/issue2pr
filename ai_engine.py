import openai
import logging
from config import OPENAI_API_KEY, AI_ENGINE
from issue_parser import IssueParser
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, github_token: str):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.engine = AI_ENGINE
        self.issue_parser = IssueParser(github_token)
        logger.info(f"Initialized AI Engine with {self.engine}")

    def generate_code(self, repo_name: str, issue_number: int) -> Dict:
        """Generate code changes based on the issue and its context."""
        try:
            logger.info(f"Generating code for issue #{issue_number} in {repo_name}")
            
            # Parse the issue and gather context
            issue_data = self.issue_parser.parse_issue(repo_name, issue_number)
            
            if self.engine == "gpt4":
                return self._generate_with_gpt4(issue_data)
            elif self.engine == "sweep":
                return self._generate_with_sweep(issue_data)
            else:
                raise ValueError(f"Unsupported AI engine: {self.engine}")

        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise

    def _generate_with_gpt4(self, issue_data: Dict) -> Dict:
        """Generate code using GPT-4 with enhanced context."""
        try:
            # Prepare the prompt with enhanced context
            prompt = self._prepare_gpt4_prompt(issue_data)
            logger.info(f"Prepared prompt: {prompt[:500]}...")  # Log first 500 chars of prompt
            
            # Make the API call
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that generates code changes based on GitHub issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Log the raw response
            content = response.choices[0].message.content
            logger.info(f"Raw AI response: {content[:500]}...")  # Log first 500 chars of response
            
            # Parse the response
            parsed_response = self._parse_gpt4_response(content)
            logger.info(f"Parsed response: {parsed_response}")
            
            return parsed_response

        except Exception as e:
            logger.error(f"Error in GPT-4 generation: {str(e)}")
            raise

    def _prepare_gpt4_prompt(self, issue_data: Dict) -> str:
        """Prepare a detailed prompt for GPT-4 with all available context."""
        prompt = f"""Issue Title: {issue_data['issue']['title']}
Issue Body: {issue_data['issue']['body']}
Labels: {', '.join(issue_data['issue']['labels'])}

Repository Context:
Description: {issue_data['context']['repository_info'].get('description', 'N/A')}
Topics: {', '.join(issue_data['context']['repository_info'].get('topics', []))}
Default Branch: {issue_data['context']['repository_info'].get('default_branch', 'N/A')}

Related Issues:
{self._format_related_issues(issue_data['context']['related_issues'])}

Code Context:
{self._format_code_context(issue_data['context']['code_context'])}

Documentation:
{self._format_documentation(issue_data['context']['documentation'])}

Please generate the necessary code changes to address this issue. Your response should follow this exact format:

## Explanation of Changes
[Provide a clear explanation of what changes will be made and why]

## Files to Modify
[List the files that need to be modified, one per line with a hyphen]

## Changes
[For each file, provide the changes in a code block. Start each file's changes with the filename in bold, followed by the code block]

## Considerations
[Any additional considerations or dependencies that need to be addressed]

Make sure to:
1. Use proper markdown formatting
2. Include complete code blocks with proper indentation
3. Separate each section with clear headers
4. Be specific about the changes needed in each file
5. Include complete implementations, not just stubs or TODOs
6. Use proper logging instead of print statements
7. Include input validation for all user-provided data
8. Add appropriate HTTP status codes for different error scenarios
9. Consider security best practices for token handling
10. Include rate limit handling and retry mechanisms
11. Add proper type hints and docstrings
12. Include unit tests where appropriate
"""
        return prompt

    def _format_related_issues(self, related_issues: List[Dict]) -> str:
        """Format related issues for the prompt."""
        if not related_issues:
            return "No related issues found."
        
        formatted = []
        for issue in related_issues:
            formatted.append(f"- #{issue['number']}: {issue['title']} ({issue['state']})")
        return "\n".join(formatted)

    def _format_code_context(self, code_context: Dict) -> str:
        """Format code context for the prompt."""
        if not code_context:
            return "No relevant code context found."
        
        formatted = []
        for path, content in code_context.items():
            formatted.append(f"File: {path}\n```\n{content}\n```")
        return "\n".join(formatted)

    def _format_documentation(self, documentation: Dict) -> str:
        """Format documentation for the prompt."""
        if not documentation:
            return "No relevant documentation found."
        
        formatted = []
        for path, content in documentation.items():
            formatted.append(f"Document: {path}\n```\n{content}\n```")
        return "\n".join(formatted)

    def _parse_gpt4_response(self, response: str) -> Dict:
        """Parse the GPT-4 response into a structured format."""
        sections = {
            'explanation': '',
            'files': '',
            'changes': {},
            'considerations': ''
        }
        
        # Split the response into lines
        lines = response.split('\n')
        current_section = None
        current_content = []
        in_code_block = False
        current_code_block = []
        current_file = None
        processed_files = set()  # Track processed files to avoid duplicates
        
        for line in lines:
            line = line.strip()
            
            # Check for code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_file:
                        sections['changes'][current_file] = '\n'.join(current_code_block)
                    current_code_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                continue
            
            if in_code_block:
                current_code_block.append(line)
                continue
            
            # Check for section markers
            if line.startswith('## Explanation'):
                current_section = 'explanation'
                continue
            elif line.startswith('## Files'):
                current_section = 'files'
                continue
            elif line.startswith('## Changes'):
                current_section = 'changes'
                continue
            elif line.startswith('## Considerations'):
                current_section = 'considerations'
                continue
            elif line.startswith('**') and line.endswith('**'):
                # Extract filename from bold text
                current_file = line.strip('*')
                if current_file not in processed_files:
                    sections['files'] += f"- {current_file}\n"
                    processed_files.add(current_file)
                continue
            
            # Add content to current section
            if current_section and not in_code_block:
                if current_section == 'explanation':
                    if line and not line.startswith('##'):
                        current_content.append(line)
                elif current_section == 'files' and line.startswith('- '):
                    file_name = line[2:].strip()
                    if file_name not in processed_files:
                        current_content.append(line)
                        processed_files.add(file_name)
                elif current_section == 'changes' and not (line.startswith('**') or line.startswith('```')):
                    current_content.append(line)
                elif current_section == 'considerations':
                    if line and not line.startswith('##'):
                        current_content.append(line)
            
            # Process the collected content
            if current_content and (not line or line.startswith('##')):
                content = '\n'.join(current_content).strip()
                if current_section == 'explanation':
                    sections['explanation'] = content
                elif current_section == 'files':
                    sections['files'] = content
                elif current_section == 'considerations':
                    sections['considerations'] = content
                current_content = []
        
        return sections

    def _generate_with_sweep(self, issue_data: Dict):
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