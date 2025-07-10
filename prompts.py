ANALYSIS_PROMPT = """
Analyze the PR diff and documentation files. Return your response as valid JSON matching this EXACT schema:

{
  "changes": [
    {
      "file": "string - exact file path",
      "action": "string - MUST be one of: replace, insert_after, insert_before, delete", 
      "find": "string - exact text to find",
      "replace": "string - replacement text (only for replace action)",
      "insert": "string - text to insert (only for insert_after/insert_before actions)"
    }
  ],
  "reasoning": "string - explanation of changes needed"
}

VALID ACTIONS:
- "replace": Find exact text and replace it
- "insert_after": Insert new text immediately after found text  
- "insert_before": Insert new text immediately before found text
- "delete": Remove the found text entirely

RULES:
1. "find" text must be exact matches from the documentation
2. Include surrounding context in "find" text for precision
3. Only use actions listed above - no variations
4. Return valid JSON only, no markdown formatting

PR Diff:
{pr_diff}

Documentation Files:
{doc_content}

Analyze and return JSON response:
"""