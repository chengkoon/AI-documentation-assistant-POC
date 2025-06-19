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
            
            # Clone the wiki repo
            clone_url = f"https://{self.github_token}@github.com/{self.repo_owner}/{self.repo_name}.wiki.git"
            result = subprocess.run([
                'git', 'clone', clone_url, self.wiki_dir
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Failed to clone wiki: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            print(f"Error cloning wiki: {e}")
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
            # Ensure wiki directory exists
            os.makedirs(self.wiki_dir, exist_ok=True)
            
            # Convert title to filename (GitHub wiki format)
            filename = page_title.replace(' ', '-').replace('/', '-')
            page_file = f"{self.wiki_dir}/{filename}.md"
            
            # Write content to file
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Configure git in the wiki directory
            subprocess.run(['git', 'config', 'user.name', 'AI Documentation Bot'], 
                         cwd=self.wiki_dir, check=True)
            subprocess.run(['git', 'config', 'user.email', 'noreply@github.com'], 
                         cwd=self.wiki_dir, check=True)
            
            # Add, commit, and push
            subprocess.run(['git', 'add', f'{filename}.md'], cwd=self.wiki_dir, check=True)
            
            commit_message = f"Update documentation: {page_title}"
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.wiki_dir, check=True)
            
            push_result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                       cwd=self.wiki_dir, capture_output=True, text=True)
            
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
            
            # Get files changed
            files_changed = subprocess.check_output([
                'git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_sha
            ], text=True).strip().split('\n')
            
            # Get ALL diff content - let AI decide what's relevant
            diff_content = subprocess.check_output([
                'git', 'show', '--format=', commit_sha
            ], text=True)
            
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
    
    # Clone wiki repository
    print("Cloning wiki repository...")
    if not wiki.clone_wiki():
        print("Failed to clone wiki repository")
        sys.exit(1)
    
    # Create page title with timestamp for uniqueness
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d")
    page_title = f"Data-Changes-{timestamp}-{args.commit_sha[:8]}"
    
    # Add metadata header to documentation
    commit_msg = changes.get('commit_message', '').split('\n')[0]  # First line only
    metadata_header = f"""# Data Changes Documentation

**Commit:** `{args.commit_sha[:8]}`  
**Date:** {timestamp}  
**Summary:** {commit_msg}

---

"""
    
    full_documentation = metadata_header + documentation
    
    # Create or update wiki page
    print(f"Creating wiki page: {page_title}")
    if wiki.create_or_update_page(page_title, full_documentation):
        wiki_url = f"https://github.com/{args.repo_owner}/{args.repo_name}/wiki/{page_title.replace(' ', '-')}"
        print(f"Documentation created: {wiki_url}")
    else:
        print("Failed to update wiki")
        sys.exit(1)

if __name__ == "__main__":
    main()