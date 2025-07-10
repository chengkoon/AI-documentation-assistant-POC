# LLM-Powered Documentation Automation Plan

## Overview
Automate documentation updates when code changes are merged to release branches using LLM analysis, while optimizing for token efficiency and reliability.

## Architecture Strategy

### Core Workflow
1. **PR merged to release branch** → triggers GitHub Actions
2. **Python script** sends PR diff + full doc content to LLM
3. **LLM returns** text-based replacements for specific files
4. **Auto-apply changes** and create documentation commit
5. **Push commit** directly to main branch or create PR
6. **Sync to Confluence** after successful commit

### Token Optimization Approach
- **Single LLM call**: Send PR diff + full doc content, get back specific replacements
- **Text-based replacements**: Use before/after text chunks instead of line numbers
- **GitHub as source of truth**: Store docs in markdown, sync to Confluence
- **Future optimization**: Embedding-based similarity search for pre-filtering relevant pages

## Implementation Phases

### Phase 1: Direct Text-Based Updates
**Goal:** Auto-apply documentation changes with single LLM call

**Features:**
- Send PR diff + full doc content to LLM in one call
- LLM returns: text-based replacements for affected files
- Auto-apply changes and create commit
- Push to main branch or create PR based on configuration

**Files to create:**
- `doc_analyzer.py` - Main script handling workflow
- `llm_client.py` - LLM API calls (Claude/OpenAI)
- `github_helper.py` - GitHub API interactions (get diff, files, commit changes)
- `text_replacer.py` - Handles text-based find/replace operations
- `config.py` - Configuration and API keys
- `requirements.txt` - Python dependencies
- `.github/workflows/doc-analysis.yml` - GitHub Actions workflow
- `prompts.py` - LLM prompt templates
- `test_analyzer.py` - Basic tests
- `README.md` - Setup and usage instructions

**LLM Input Format:**
```
PR Diff: [full code diff]

Current Documentation Files:
--- docs/authentication.md ---
[full file content]

--- docs/api-security.md ---
[full file content]

Please analyze and return specific text replacements needed.
```

**LLM Output Format:**
```json
{
  "changes": [
    {
      "file": "docs/authentication.md",
      "action": "replace",
      "find": "## API Authentication\n\nCurrently supports basic auth only.",
      "replace": "## API Authentication\n\nSupports basic auth and OAuth 2.0. For OAuth setup:\n\n1. Register your app\n2. Get client credentials\n3. Use authorization flow"
    },
    {
      "file": "docs/api-security.md", 
      "action": "insert_after",
      "find": "### Rate Limits\n\nAPI calls are limited to 1000/hour.",
      "insert": "\n\n### Error Handling\n\nAll errors return standard HTTP codes with JSON responses."
    }
  ],
  "reasoning": "Added JWT support in auth.py requires documentation updates for new OAuth flow..."
}
```

### Phase 2: Add Safety & Validation
**Goal:** Make auto-updates more reliable and safe

**Features:**
- Validate all "find" text exists before applying changes
- Add dry-run mode for testing
- Implement rollback mechanism
- Add change confidence scoring
- Log all changes with reasoning

**Safety mechanisms:**
- Pre-validate all text replacements
- Backup original files before changes
- Detailed logging of all operations
- Ability to revert commits if needed

### Phase 3: Optimization & Intelligence
**Goal:** Reduce token usage and improve accuracy

**Features:**
- Add embedding-based pre-filtering of relevant documentation pages
- Implement smarter chunking for large documentation sets
- Add learning from previous successful/failed changes
- Optimize prompts based on results

### Phase 4: Advanced Features (Future)
**Goal:** Handle complex documentation scenarios

**Features:**
- Support for multi-file changes with dependencies
- Automatic creation of new documentation pages
- Integration with documentation style guides
- Advanced conflict resolution

## Key Safety Features (All Phases)

- **Text validation** before applying any changes (ensure "find" text exists)
- **Dry-run mode** for testing without making changes
- **Detailed logging** of all LLM decisions and text replacements
- **Rollback mechanism** for bad changes (Git revert capability)
- **Backup strategy** - save original files before modification
- **Change validation** - verify replacements don't break markdown formatting
- **Human override** always available through manual commits

## Text-Based Replacement Strategy

**Instead of line numbers:**
```
"append {{new documentation}} between lines 50 and 51"
"delete lines 20 to 23"
```

**Use text chunks:**
```json
{
  "action": "replace",
  "find": "## API Authentication\n\nCurrently supports basic auth only.",
  "replace": "## API Authentication\n\nSupports basic auth and OAuth 2.0..."
}
```

**Benefits:**
- More reliable than line numbers
- Can validate "find" text exists before replacing
- Less prone to off-by-one errors
- Easier to debug when something goes wrong

## Future Optimization: Embedding-Based Similarity

**Concept:** Use AI embeddings to find semantically similar content without keyword matching

**How it works:**
1. Convert code diff into vector embedding
2. Convert each doc page title/intro into vectors
3. Find pages with vectors most similar to code diff
4. Only send top N most relevant pages to LLM

**Benefits:**
- Catches semantic relationships ("JWT" relates to "Authentication")
- Reduces tokens by 70-80% through pre-filtering
- Works even when code uses different terminology than docs

**Implementation:**
- Use OpenAI's embedding API or local embeddings with `sentence-transformers`
- Calculate cosine similarity between diff and doc embeddings
- Set threshold for relevance scoring

## Documentation Sync Strategy

**Source of Truth:** GitHub repository (markdown files)
**Read-Only Display:** Confluence (for non-developers)

**Workflow:**
1. Developers update markdown in GitHub
2. After PR merge, auto-sync to Confluence
3. Business team can comment on Confluence
4. Comments trigger GitHub issues for developer action
5. Developers update markdown source, cycle repeats

**Benefits:**
- Version control for documentation
- LLM-friendly markdown format
- Separation of concerns (devs use GitHub, business uses Confluence)
- Single source of truth prevents drift

## Critical Considerations

**Reliability Challenges:**
- LLM consistency in identifying relevant changes
- Handling edge cases and ambiguous code changes
- Maintaining quality when auto-applying changes

**Maintenance Overhead:**
- Debugging LLM reasoning when things go wrong
- Keeping prompts updated as codebase evolves
- Monitoring for false positives/negatives

**Team Adoption:**
- Training team on new workflow
- Handling exceptions and manual overrides
- Ensuring business team understands GitHub/Confluence split

## Success Metrics

**Phase 1:**
- Accuracy of text replacements (successful vs failed)
- Time saved in manual doc updates
- Token usage per documentation update
- Number of successful auto-commits vs rollbacks

**Phase 2:**
- Validation accuracy (catching bad replacements before apply)
- Dry-run vs actual run success rates
- Time from code change to doc commit

**Phase 3+:**
- Token usage reduction from embedding pre-filtering
- Overall documentation freshness and accuracy
- Developer satisfaction with auto-updates

## Getting Started

1. **Set up Phase 1** with direct text-based updates
2. **Test extensively** in dry-run mode on your codebase
3. **Validate text replacement accuracy** before enabling auto-commits
4. **Start with low-risk changes** (additions rather than deletions)
5. **Monitor commit quality** and add rollback procedures
6. **Gradually expand** to more complex changes as confidence builds

Remember: Start with robust validation, then enable automation incrementally.