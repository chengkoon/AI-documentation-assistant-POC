#!/usr/bin/env python3

import re
import json

def test_json_parsing():
    # Test the JSON parsing logic with a sample response similar to what Claude returned
    test_response = '''```json
{
  "needs_documentation": true,
  "reasoning": "Test",
  "documentation_strategy": {
    "action": "update_existing_page",
    "target_pages": ["Database Schema"]
  }
}
```'''

    print("Original response:")
    print(repr(test_response))
    print()

    # Apply the same cleaning logic from our script
    cleaned_result = test_response.strip()
    
    if cleaned_result.startswith('```json'):
        json_match = re.search(r'```json\s*\n(.*?)\n```', cleaned_result, re.DOTALL)
        if json_match:
            cleaned_result = json_match.group(1).strip()
        else:
            cleaned_result = cleaned_result.replace('```json', '').replace('```', '').strip()

    print("Cleaned result:")
    print(repr(cleaned_result))
    print()

    try:
        strategy = json.loads(cleaned_result)
        print("✅ Parsed successfully!")
        print(f"Action: {strategy['documentation_strategy']['action']}")
        print(f"Target pages: {strategy['documentation_strategy']['target_pages']}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False

if __name__ == "__main__":
    test_json_parsing()
