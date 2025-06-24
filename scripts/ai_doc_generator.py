#!/usr/bin/env python3
"""
AI Documentation Generator for Database Schema Changes
Analyzes git commits and generates Confluence documentation
"""

import os
import sys
import json
import requests
import argparse
import subprocess
from typing import Dict, List, Optional

class GitHubWikiAPI:
    def __init__(self, repo_owner: str, repo_name: str, github_token: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.wiki_repo_url = f"https://github.com/{repo_owner}/{repo_name}.wiki.git"
        self.wiki_dir = "/tmp/wiki_clone"
    
    def clone_wiki(self) -> bool:
        """Clone the GitHub wiki repository"""
        try:
            # Clean up any existing clone
            subprocess.run(['rm', '-rf', self.wiki_dir], check=False)
            
            # Configure git globally
            subprocess.run([
                'git', 'config', '--global', 'user.name', 'AI Documentation Bot'
            ], check=True)
            subprocess.run([
                'git', 'config', '--global', 'user.email', 'noreply@github.com'
            ], check=True)
            
            # Configure git to use token via credential helper (official method)
            subprocess.run([
                'git', 'config', '--global', 'credential.helper', 'store'
            ], check=True)
            
            # Create credentials file with token (official method)
            # Format from GitHub docs: username is required but not used for auth, token is the password
            credentials_content = f"https://github-actions:{self.github_token}@github.com"
            credentials_path = os.path.expanduser("~/.git-credentials")
            with open(credentials_path, 'w') as f:
                f.write(credentials_content + '\n')
            os.chmod(credentials_path, 0o600)  # Secure file permissions
            
            # Set environment variables to prevent interactive prompts
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            # Clone using standard HTTPS URL (official method)
            clone_url = f"https://github.com/{self.repo_owner}/{self.repo_name}.wiki.git"
            result = subprocess.run([
                'git', 'clone', clone_url, self.wiki_dir
            ], capture_output=True, text=True, env=env)
            
            if result.returncode != 0:
                print(f"Clone failed: {result.stderr}")
                # Try to create wiki if it doesn't exist
                return self._create_wiki_if_not_exists()
            
            return True
        except Exception as e:
            print(f"Error cloning wiki: {e}")
            return False
    
    def _create_wiki_if_not_exists(self) -> bool:
        """Create wiki repository if it doesn't exist"""
        try:
            print("Wiki doesn't exist, creating initial wiki...")
            # Initialize a new git repo
            os.makedirs(self.wiki_dir, exist_ok=True)
            
            # Configure git in the wiki directory
            subprocess.run(['git', 'init'], cwd=self.wiki_dir, check=True)
            subprocess.run(['git', 'config', 'user.name', 'AI Documentation Bot'], 
                         cwd=self.wiki_dir, check=True)
            subprocess.run(['git', 'config', 'user.email', 'noreply@github.com'], 
                         cwd=self.wiki_dir, check=True)
            
            # Create initial Home page
            home_content = """# Welcome to the Documentation Wiki

This wiki contains automatically generated documentation for data changes in this repository.

## Pages

- Data change documentation will appear here automatically when PRs are merged.
"""
            with open(f"{self.wiki_dir}/Home.md", 'w') as f:
                f.write(home_content)
            
            # Add remote using standard HTTPS URL (credentials already configured globally)
            remote_url = f"https://github.com/{self.repo_owner}/{self.repo_name}.wiki.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                         cwd=self.wiki_dir, check=True)
            
            # Set up environment to prevent prompts
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            # Initial commit and push
            subprocess.run(['git', 'add', '.'], cwd=self.wiki_dir, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial wiki setup'], 
                         cwd=self.wiki_dir, check=True)
            
            # Push using standard method with credential helper
            result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], 
                                  cwd=self.wiki_dir, capture_output=True, text=True, env=env)
            
            if result.returncode != 0:
                print(f"Failed to create wiki: {result.stderr}")
                return False
            
            print("Wiki created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating wiki: {e}")
            return False
    
    def get_page(self, page_title: str) -> Optional[str]:
        """Get content of a wiki page"""
        try:
            page_file = f"{self.wiki_dir}/{page_title.replace(' ', '-')}.md"
            if os.path.exists(page_file):
                with open(page_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading wiki page: {e}")
            return None
    
    def create_or_update_page(self, page_title: str, content: str) -> bool:
        """Create or update a wiki page"""
        try:
            # Convert title to filename (GitHub wiki format)
            filename = page_title.replace(' ', '-').replace('/', '-')
            page_file = f"{self.wiki_dir}/{filename}.md"
            
            # Write content to file
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add and commit
            subprocess.run(['git', 'add', f'{filename}.md'], cwd=self.wiki_dir, check=True)
            
            commit_message = f"Update documentation: {page_title}"
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.wiki_dir, check=True)
            
            # Set up environment to prevent interactive prompts
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            # Push using credential helper (credentials already configured)
            push_result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                       cwd=self.wiki_dir, capture_output=True, text=True, env=env)
            
            if push_result.returncode != 0:
                print(f"Failed to push to wiki: {push_result.stderr}")
                return False
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"Error updating wiki page: {e}")
            return False

    def analyze_wiki_structure(self) -> Dict:
        """Analyze the current wiki structure and content to understand existing documentation"""
        try:
            wiki_analysis = {
                'pages': {},
                'structure': {},
                'topics_covered': [],
                'schema_pages': [],
                'api_pages': [],
                'data_flow_pages': []
            }
            
            # Get all markdown files in the wiki
            wiki_files = []
            for root, dirs, files in os.walk(self.wiki_dir):
                for file in files:
                    if file.endswith('.md'):
                        wiki_files.append(file)
            
            # Analyze each page
            for file in wiki_files:
                page_name = file.replace('.md', '').replace('-', ' ')
                file_path = os.path.join(self.wiki_dir, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Store page content and metadata
                    wiki_analysis['pages'][page_name] = {
                        'filename': file,
                        'content': content,
                        'length': len(content),
                        'has_schema_content': self._contains_schema_content(content),
                        'has_api_content': self._contains_api_content(content),
                        'has_data_flow_content': self._contains_data_flow_content(content),
                        'last_updated': self._extract_last_update_date(content)
                    }
                    
                    # Categorize pages
                    if self._contains_schema_content(content):
                        wiki_analysis['schema_pages'].append(page_name)
                    if self._contains_api_content(content):
                        wiki_analysis['api_pages'].append(page_name)
                    if self._contains_data_flow_content(content):
                        wiki_analysis['data_flow_pages'].append(page_name)
                        
                except Exception as e:
                    print(f"Error reading wiki page {file}: {e}")
            
            return wiki_analysis
            
        except Exception as e:
            print(f"Error analyzing wiki structure: {e}")
            return {'pages': {}, 'structure': {}, 'topics_covered': []}
    
    def _contains_schema_content(self, content: str) -> bool:
        """Check if content contains database schema related information"""
        schema_keywords = [
            'CREATE TABLE', 'ALTER TABLE', 'ADD COLUMN', 'DROP COLUMN',
            'PRIMARY KEY', 'FOREIGN KEY', 'INDEX', 'CONSTRAINT',
            'database schema', 'table structure', 'column', 'field'
        ]
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in schema_keywords)
    
    def _contains_api_content(self, content: str) -> bool:
        """Check if content contains API related information"""
        api_keywords = [
            'API', 'endpoint', 'JSON', 'response', 'request',
            'REST', 'GraphQL', '/api/', 'GET', 'POST', 'PUT', 'DELETE'
        ]
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in api_keywords)
    
    def _contains_data_flow_content(self, content: str) -> bool:
        """Check if content contains data flow related information"""
        flow_keywords = [
            'data flow', 'data pipeline', 'transformation', 'mapping',
            'service', 'controller', 'repository', 'entity'
        ]
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in flow_keywords)
    
    def _extract_last_update_date(self, content: str) -> Optional[str]:
        """Extract the last update date from content if available"""
        import re
        # Look for common date patterns
        date_patterns = [
            r'\*\*Date:\*\*\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2})',
            r'Update\s+([0-9]{4}-[0-9]{2}-[0-9]{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None

    def intelligent_documentation_strategy(self, changes: Dict, wiki_analysis: Dict, ai_generator) -> Dict:
        """Use AI to determine the intelligent documentation strategy based on changes and current wiki state"""
        
        # Create a comprehensive prompt for the AI to analyze the situation
        strategy_prompt = f"""
        You are an intelligent documentation system. Analyze the following code changes against the current wiki state and determine the optimal documentation strategy.

        **CURRENT WIKI STRUCTURE:**
        {self._format_wiki_summary(wiki_analysis)}

        **CODE CHANGES TO ANALYZE:**
        Commit Message: {changes.get('commit_message', '')}
        Files Changed: {', '.join(changes.get('files_changed', []))}
        
        CODE DIFF:
        {changes.get('diff_content', '')[:12000]}

        **YOUR TASK:**
        Analyze whether these changes introduce NEW data-related concepts that are NOT already documented in the wiki.

        **EVALUATION CRITERIA:**
        1. **Schema Changes**: New tables, columns, relationships not already documented
        2. **API Changes**: New endpoints, response formats not already covered
        3. **Data Flow Changes**: New business logic, data transformations not documented
        4. **Configuration Changes**: Database settings, connections not covered

        **RESPOND WITH A JSON OBJECT (no markdown formatting, just pure JSON):**
        {{
            "needs_documentation": true/false,
            "reasoning": "Explain why documentation is/isn't needed",
            "changes_summary": "Brief summary of what's actually new",
            "documentation_strategy": {{
                "action": "create_new_page" | "update_existing_page" | "append_to_page" | "update_multiple_pages",
                "target_pages": ["page1", "page2"] or ["new_page_name"],
                "content_type": "schema" | "api" | "data_flow" | "mixed",
                "priority": "high" | "medium" | "low"
            }},
            "page_recommendations": {{
                "primary_page": "recommended page name",
                "sections_to_update": ["section1", "section2"],
                "new_sections_needed": ["new_section1"]
            }}
        }}

        **IMPORTANT:**
        - Only recommend documentation if there are GENUINELY NEW data concepts not already covered
        - Be specific about which wiki pages should be updated based on their current content
        - Consider the existing wiki structure when making recommendations
        - If changes are minor updates to existing documented features, set needs_documentation to false
        - Return ONLY the JSON object, no additional text or markdown formatting
        """
        
        strategy_result = ai_generator._call_ai_service(strategy_prompt)
        
        try:
            # Parse the AI response as JSON, handling markdown code blocks
            import json
            import re
            
            # Clean the response by extracting JSON from markdown code blocks if present
            cleaned_result = strategy_result.strip()
            
            # Check if response is wrapped in markdown code blocks
            if cleaned_result.startswith('```json'):
                # Extract JSON from markdown code block
                json_match = re.search(r'```json\s*\n(.*?)\n```', cleaned_result, re.DOTALL)
                if json_match:
                    cleaned_result = json_match.group(1).strip()
                else:
                    # Fallback: remove the opening ```json and closing ```
                    cleaned_result = cleaned_result.replace('```json', '').replace('```', '').strip()
            elif cleaned_result.startswith('```'):
                # Handle generic code blocks
                cleaned_result = re.sub(r'^```[^\n]*\n', '', cleaned_result)
                cleaned_result = re.sub(r'\n```$', '', cleaned_result)
                cleaned_result = cleaned_result.strip()
            
            strategy = json.loads(cleaned_result)
            return strategy
        except json.JSONDecodeError as e:
            print(f"Error parsing AI strategy response: {strategy_result}")
            print(f"JSON parsing error: {e}")
            # Fallback to simple analysis
            return {
                "needs_documentation": True,
                "reasoning": "Fallback analysis - assuming documentation needed",
                "documentation_strategy": {
                    "action": "create_new_page",
                    "target_pages": ["Data-Changes-Fallback"],
                    "content_type": "mixed",
                    "priority": "medium"
                }
            }

    def _format_wiki_summary(self, wiki_analysis: Dict) -> str:
        """Format wiki analysis for AI consumption"""
        summary = "EXISTING WIKI PAGES:\n\n"
        
        for page_name, page_info in wiki_analysis['pages'].items():
            summary += f"**{page_name}** ({page_info['length']} chars)\n"
            summary += f"  - Contains Schema Content: {page_info['has_schema_content']}\n"
            summary += f"  - Contains API Content: {page_info['has_api_content']}\n" 
            summary += f"  - Contains Data Flow Content: {page_info['has_data_flow_content']}\n"
            if page_info['last_updated']:
                summary += f"  - Last Updated: {page_info['last_updated']}\n"
            summary += f"  - Content Preview: {page_info['content'][:200]}...\n\n"
        
        summary += f"\nSCHEMA PAGES: {', '.join(wiki_analysis['schema_pages'])}\n"
        summary += f"API PAGES: {', '.join(wiki_analysis['api_pages'])}\n"
        summary += f"DATA FLOW PAGES: {', '.join(wiki_analysis['data_flow_pages'])}\n"
        
        return summary

    def execute_intelligent_documentation(self, strategy: Dict, documentation_content: str, changes: Dict, ai_generator) -> bool:
        """Execute the documentation strategy determined by AI"""
        try:
            action = strategy['documentation_strategy']['action']
            target_pages = strategy['documentation_strategy']['target_pages']
            
            if action == "create_new_page":
                return self._create_new_intelligent_page(target_pages[0], documentation_content, changes, strategy)
                
            elif action == "update_existing_page":
                return self._update_existing_intelligent_page(target_pages[0], documentation_content, changes, strategy, ai_generator)
                
            elif action == "append_to_page":
                return self._append_to_intelligent_page(target_pages[0], documentation_content, changes, strategy)
                
            elif action == "update_multiple_pages":
                success = True
                for page in target_pages:
                    if not self._update_existing_intelligent_page(page, documentation_content, changes, strategy, ai_generator):
                        success = False
                return success
                
            else:
                print(f"Unknown documentation action: {action}")
                return False
                
        except Exception as e:
            print(f"Error executing intelligent documentation strategy: {e}")
            return False

    def _create_new_intelligent_page(self, page_name: str, content: str, changes: Dict, strategy: Dict) -> bool:
        """Create a new page with intelligent structure based on AI strategy"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d")
        commit_sha = changes.get('commit_message', '')[:8] if changes.get('commit_message') else 'unknown'
        
        page_header = f"""# {page_name}

**Created:** {timestamp}  
**Trigger:** {strategy.get('reasoning', 'Data changes detected')}  
**Content Type:** {strategy['documentation_strategy'].get('content_type', 'mixed')}

---

"""
        
        full_content = page_header + content
        return self.create_or_update_page(page_name, full_content)

    def _update_existing_intelligent_page(self, page_name: str, new_content: str, changes: Dict, strategy: Dict, ai_generator) -> bool:
        """Intelligently update an existing page by merging new content"""
        existing_content = self.get_page(page_name)
        
        if not existing_content:
            # Page doesn't exist, create it
            return self._create_new_intelligent_page(page_name, new_content, changes, strategy)
        
        # Use AI to intelligently merge content
        merge_prompt = f"""
        You need to intelligently merge new documentation content into an existing wiki page.

        **EXISTING PAGE CONTENT:**
        {existing_content}

        **NEW CONTENT TO INTEGRATE:**
        {new_content}

        **MERGE STRATEGY:**
        - Update relevant sections with new information
        - Add new sections if the content covers new topics
        - Maintain existing structure and organization
        - Add update timestamps where appropriate
        - Avoid duplication

        **RETURN THE COMPLETE UPDATED PAGE CONTENT:**
        """
        
        merged_content = ai_generator._call_ai_service(merge_prompt)
        return self.create_or_update_page(page_name, merged_content)

    def _append_to_intelligent_page(self, page_name: str, content: str, changes: Dict, strategy: Dict) -> bool:
        """Append content to an existing page with intelligent formatting"""
        existing_content = self.get_page(page_name) or f"# {page_name}\n\n"
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_sha = changes.get('commit_message', '')[:8] if changes.get('commit_message') else 'unknown'
        
        append_section = f"""
---

## Update {timestamp} - {strategy.get('changes_summary', 'Data Changes')}

{content}

"""
        
        updated_content = existing_content + append_section
        return self.create_or_update_page(page_name, updated_content)

class AIDocumentationGenerator:
    def __init__(self, ai_api_key: str, ai_provider: str = "openai"):
        self.ai_api_key = ai_api_key
        self.ai_provider = ai_provider
        
    def get_git_changes(self, commit_sha: str) -> Dict:
        """Get git diff and commit info for ALL changed files"""
        try:
            # Get commit message
            commit_msg = subprocess.check_output([
                'git', 'log', '-1', '--pretty=%B', commit_sha
            ], text=True).strip()
            
            # Get files changed - try multiple approaches
            try:
                files_changed = subprocess.check_output([
                    'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_sha
                ], text=True).strip().split('\n')
            except subprocess.CalledProcessError:
                # Fallback: compare with previous commit
                files_changed = subprocess.check_output([
                    'git', 'diff', '--name-only', 'HEAD~1', 'HEAD'
                ], text=True).strip().split('\n')
            
            # Clean up empty strings from the list
            files_changed = [f for f in files_changed if f.strip()]
            
            # Get diff content - try multiple approaches
            diff_content = ""
            try:
                # Primary approach: get diff for specific commit
                diff_content = subprocess.check_output([
                    'git', 'show', '--format=', commit_sha
                ], text=True)
            except subprocess.CalledProcessError:
                try:
                    # Fallback: compare with previous commit
                    diff_content = subprocess.check_output([
                        'git', 'diff', 'HEAD~1', 'HEAD'
                    ], text=True)
                except subprocess.CalledProcessError:
                    print("Warning: Could not get diff content")
            
            # Debug output
            print(f"Commit: {commit_sha}")
            print(f"Files changed: {files_changed}")
            print(f"Diff content length: {len(diff_content)} characters")
            
            return {
                'commit_message': commit_msg,
                'files_changed': files_changed,
                'diff_content': diff_content
            }
        except subprocess.CalledProcessError as e:
            print(f"Error getting git changes: {e}")
            return {}
    
    def analyze_with_ai(self, changes: Dict) -> Optional[str]:
        """Send ALL changes to AI for intelligent analysis of data-related impacts"""
        if not changes.get('diff_content'):
            print("No code changes found")
            return None
            
        # Two-stage AI analysis: first determine relevance, then generate documentation
        relevance_prompt = f"""
        Analyze the following code changes to determine if they contain any data-related modifications that would benefit from documentation.
        
        Commit Message: {changes.get('commit_message', '')}
        Files Changed: {', '.join(changes.get('files_changed', []))}
        
        CODE CHANGES:
        {changes.get('diff_content', '')[:8000]}  # Truncate for initial analysis
        
        Look for ANY of these patterns (regardless of file type or naming convention):
        
        1. **Database Schema Changes**: CREATE TABLE, ALTER TABLE, ADD COLUMN, DROP COLUMN, CREATE INDEX
        2. **SQL Query Changes**: SELECT statements, WHERE clauses, JOIN operations, new queries, modified queries
        3. **Data Mapping**: Object mapping, field assignments, data transformation code
        4. **API Response Changes**: New fields in JSON responses, modified data structures
        5. **Data Processing Logic**: How data is filtered, aggregated, or transformed
        6. **Configuration Changes**: Database connections, data source settings
        7. **Migration Scripts**: Data migration or cleanup scripts
        
        Respond with either:
        - "RELEVANT" if you find data-related changes that could benefit from documentation
        - "NOT_RELEVANT" if the changes are purely UI, styling, logging, or other non-data related
        
        Be inclusive - if there's any doubt, respond with "RELEVANT".
        """
        
        relevance_result = self._call_ai_service(relevance_prompt)
        
        if not relevance_result or "NOT_RELEVANT" in relevance_result:
            print("AI determined changes are not data-related")
            return None
            
        print("AI detected data-related changes, generating documentation...")
        
        # Full documentation analysis
        documentation_prompt = f"""
        The following code changes contain data-related modifications. Analyze them comprehensively to generate documentation that helps with data governance and understanding.
        
        Commit Message: {changes.get('commit_message', '')}
        Files Changed: {', '.join(changes.get('files_changed', []))}
        
        FULL CODE CHANGES:
        {changes.get('diff_content', '')}
        
        Your goal is to answer the key data governance questions:
        - **WHY was this column/field added?** (business purpose)
        - **HOW is this data used?** (data flow through the application)
        - **WHAT does this change mean for data consumers?** (API, reports, etc.)
        
        Analyze the changes and provide documentation covering relevant sections:
        
        **1. SUMMARY**
        - Brief overview of what changed from a data perspective
        - Business context (infer from commit message and code patterns)
        
        **2. DATABASE SCHEMA CHANGES** (if any)
        - New tables, columns, indexes with their business purpose
        - Data types and constraints and why they were chosen
        - Relationships to existing data
        
        **3. DATA QUERY CHANGES** (if any)
        - New or modified SQL queries and their purpose
        - Changes in data selection criteria (WHERE, JOIN, etc.)
        - Performance implications or query optimization
        
        **4. DATA FLOW AND USAGE** (if any)
        - How data moves through the application layers
        - How results are mapped, transformed, or processed
        - Business logic that consumes this data
        
        **5. API AND CONSUMER IMPACT** (if any)
        - New fields exposed to API consumers
        - Changes in response structures or data formats
        - Backward compatibility considerations
        
        **6. DATA GOVERNANCE NOTES**
        - Purpose and meaning of new data elements
        - Data quality or validation rules
        - Access patterns or security considerations
        
        Focus on business context and practical usage. Explain WHY the changes were made and HOW the data will be used.
        Format as **Markdown** with clear headers and sections (##, ###).
        Use tables for structured data like column definitions.
        
        If after this detailed analysis you determine no significant documentation is needed, respond with "NO_DOCUMENTATION_NEEDED".
        """
        
        return self._call_ai_service(documentation_prompt)
    
    def _call_ai_service(self, prompt: str) -> str:
        """Call the configured AI service"""
        if self.ai_provider == "openai":
            return self._call_openai(prompt)
        elif self.ai_provider == "anthropic":
            return self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.ai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3000,
            "temperature": 0.2
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.ai_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print(response.text[:10000])
            return response.json()["content"][0]["text"]
        else:
            print(f"Anthropic API error: {response.status_code} - {response.text}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Generate AI documentation for database changes')
    parser.add_argument('--commit-sha', required=True, help='Git commit SHA to analyze')
    parser.add_argument('--ai-provider', default='anthropic', choices=['openai', 'anthropic'])
    parser.add_argument('--repo-owner', help='GitHub repository owner (e.g., "mycompany")')
    parser.add_argument('--repo-name', help='GitHub repository name (e.g., "myapp")')
    parser.add_argument('--dry-run', action='store_true', help='Print documentation without updating wiki')
    
    args = parser.parse_args()
    
    # Get environment variables
    ai_api_key = os.getenv('AI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    
    # Extract repo info from GitHub context if not provided
    if not args.repo_owner or not args.repo_name:
        github_repository = os.getenv('GITHUB_REPOSITORY', '')
        if '/' in github_repository:
            args.repo_owner, args.repo_name = github_repository.split('/', 1)
        else:
            print("Error: Could not determine repository owner/name")
            sys.exit(1)
    
    if not ai_api_key:
        print("Error: AI_API_KEY or ANTHROPIC_API_KEY environment variable required")
        sys.exit(1)
    
    # Initialize AI generator
    ai_gen = AIDocumentationGenerator(ai_api_key, args.ai_provider)
    
    # Get git changes
    print(f"Analyzing commit {args.commit_sha}...")
    changes = ai_gen.get_git_changes(args.commit_sha)
    
    if not changes or not changes.get('diff_content'):
        print("No changes found")
        sys.exit(0)
    
    # Analyze with AI
    print("Sending to AI for analysis...")
    documentation = ai_gen.analyze_with_ai(changes)
    
    if not documentation or documentation.strip() == "NO_DOCUMENTATION_NEEDED":
        print("AI determined no documentation update needed")
        sys.exit(0)
    
    if args.dry_run:
        print("Generated documentation:")
        print("=" * 50)
        print(documentation)
        sys.exit(0)
    
    # Update GitHub Wiki
    if not github_token:
        print("Missing GITHUB_TOKEN, printing documentation instead:")
        print(documentation)
        sys.exit(0)
    
    wiki = GitHubWikiAPI(args.repo_owner, args.repo_name, github_token)
    
    # Clone wiki repository to analyze current state
    print("Cloning wiki repository...")
    if not wiki.clone_wiki():
        print("Failed to clone wiki repository")
        sys.exit(1)
    
    # STEP 1: Analyze current wiki structure and content
    print("Analyzing current wiki structure...")
    wiki_analysis = wiki.analyze_wiki_structure()
    print(f"Found {len(wiki_analysis['pages'])} existing pages")
    
    # STEP 2: Use AI to determine if documentation is needed and strategy
    print("Determining intelligent documentation strategy...")
    strategy = wiki.intelligent_documentation_strategy(changes, wiki_analysis, ai_gen)
    
    print(f"AI Strategy: {strategy.get('reasoning', 'No reasoning provided')}")
    
    if not strategy.get('needs_documentation', False):
        print("AI determined no new documentation is needed")
        print(f"Reason: {strategy.get('reasoning', 'Changes already covered in existing documentation')}")
        sys.exit(0)
    
    # STEP 3: Generate documentation content for the new changes
    print("Generating documentation for new changes...")
    documentation = ai_gen.analyze_with_ai(changes)
    
    if not documentation or documentation.strip() == "NO_DOCUMENTATION_NEEDED":
        print("AI content generator determined no documentation update needed")
        sys.exit(0)
    
    # STEP 4: Execute the intelligent documentation strategy
    print(f"Executing documentation strategy: {strategy['documentation_strategy']['action']}")
    print(f"Target pages: {strategy['documentation_strategy']['target_pages']}")
    
    if wiki.execute_intelligent_documentation(strategy, documentation, changes, ai_gen):
        primary_page = strategy.get('page_recommendations', {}).get('primary_page', 
                                  strategy['documentation_strategy']['target_pages'][0])
        wiki_url = f"https://github.com/{args.repo_owner}/{args.repo_name}/wiki/{primary_page.replace(' ', '-')}"
        print(f"Documentation successfully updated: {wiki_url}")
        print(f"Strategy executed: {strategy['documentation_strategy']['action']}")
    else:
        print("Failed to execute documentation strategy")
        sys.exit(1)

if __name__ == "__main__":
    main()