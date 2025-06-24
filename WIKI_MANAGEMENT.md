# Intelligent AI Documentation System

## Overview

This system uses AI to intelligently analyze your repository's existing wiki documentation and only create/update documentation for genuinely NEW data-related changes that aren't already covered.

## How It Works

### 1. **Wiki Analysis Phase**
The system first analyzes your existing wiki to understand:
- What documentation already exists
- How it's organized (schema docs, API docs, data flow docs)
- What data concepts are already covered
- When pages were last updated

### 2. **Intelligent Gap Detection**
The AI compares your PR changes against existing documentation to identify:
- ✅ **New data concepts** that need documentation
- ❌ **Already documented features** that don't need new docs
- 🔄 **Existing features** that need updates

### 3. **Smart Documentation Strategy**
Based on the analysis, the AI chooses the optimal approach:

| Strategy | When Used | Example |
|----------|-----------|---------|
| `create_new_page` | Completely new feature/concept | New microservice, new data domain |
| `update_existing_page` | Adding to existing documented area | New column in documented table |
| `append_to_page` | Related but separate addition | New endpoint in existing API |
| `update_multiple_pages` | Cross-cutting changes | Schema change affecting multiple APIs |

### 4. **Intelligent Execution**
The system updates the right pages with contextually appropriate content.

## What Gets Documented

The AI looks for data-related changes including:

### ✅ **Always Documented**
- New database tables, columns, indexes
- New API endpoints or response formats
- New data transformation logic
- Database configuration changes
- Data migration scripts

### ❓ **Smart Detection**
- Modified queries (only if significantly different)
- Updated data mappings (only if business logic changes)
- API modifications (only if response structure changes)

### ❌ **Never Documented**
- UI styling changes
- Log message updates
- Code refactoring without data impact
- Comment changes

## Example Scenarios

### Scenario 1: New Feature
**Change:** Add `user_preferences` table
**AI Decision:** "New table not documented anywhere - CREATE new page"
**Result:** Creates "User Preferences Schema" page

### Scenario 2: Existing Feature Update
**Change:** Add column to existing `users` table (already documented)
**AI Decision:** "Users table already documented - UPDATE existing page"
**Result:** Updates "Database Schema" page with new column

### Scenario 3: Minor Change
**Change:** Update log message format
**AI Decision:** "No data impact, already covered in logging docs - SKIP"
**Result:** No documentation created

### Scenario 4: API Extension
**Change:** Add new endpoint to existing API
**AI Decision:** "API documented but this endpoint is new - APPEND to API page"
**Result:** Adds new endpoint section to "API Documentation"

## Configuration

### GitHub Actions Integration

The system runs automatically on PR merges:

```yaml
- name: Generate AI Documentation
  env:
    AI_API_KEY: ${{ secrets.AI_API_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python scripts/ai_doc_generator.py \
      --commit-sha ${{ github.event.pull_request.head.sha }} \
      --ai-provider anthropic
```

### Manual Usage

```bash
# Analyze specific commit
python scripts/ai_doc_generator.py \
  --commit-sha abc123 \
  --ai-provider anthropic

# Dry run to see what would be documented
python scripts/ai_doc_generator.py \
  --commit-sha abc123 \
  --dry-run
```

## AI Decision Process

The system uses a sophisticated AI prompt that:

1. **Analyzes existing wiki structure**
   ```
   Found 5 existing pages:
   - Database Schema (contains table docs)
   - API Documentation (contains endpoint docs)  
   - Data Flow (contains service integration docs)
   ```

2. **Evaluates code changes**
   ```
   PR Changes: Added user_preferences table
   Files: schema.sql, UserPreferences.java, UserController.java
   ```

3. **Makes intelligent decision**
   ```json
   {
     "needs_documentation": true,
     "reasoning": "New user_preferences table introduces new data concept not covered in existing Database Schema page",
     "documentation_strategy": {
       "action": "update_existing_page",
       "target_pages": ["Database Schema"],
       "content_type": "schema"
     }
   }
   ```

## Benefits

### 🎯 **Precision**
- Only documents genuinely new concepts
- Avoids duplicate or redundant documentation
- Understands context of existing docs

### 🧠 **Intelligence** 
- Learns your documentation patterns
- Maintains consistent organization
- Makes contextually appropriate decisions

### 🔄 **Maintenance**
- Keeps documentation up-to-date
- Reduces manual overhead
- Prevents documentation drift

### 📊 **Quality**
- Consistent documentation structure
- Comprehensive coverage of data changes
- Business context included automatically

## Troubleshooting

### If Documentation Isn't Created
Check the workflow logs for:
- "AI determined no new documentation is needed"
- "Changes already covered in existing documentation"

This is usually correct - the AI found your changes are already documented!

### If Wrong Page Updated
The AI makes decisions based on existing content. You can:
- Improve existing page organization
- Add clearer section headers
- The AI will learn from the improved structure

### Manual Override
If you need to force documentation:
```bash
# This bypasses the intelligent analysis
python scripts/ai_doc_generator.py \
  --commit-sha abc123 \
  --force-documentation
```

## Future Enhancements

- **Learning from feedback**: Track which decisions were correct
- **Custom rules**: Organization-specific documentation patterns  
- **Integration analytics**: Metrics on documentation coverage
- **Multi-repository analysis**: Cross-repo data relationship documentation