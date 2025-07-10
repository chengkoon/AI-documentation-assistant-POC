# LLM-Powered Documentation Automation Plan

## Overview
Automate documentation updates when code changes are merged to release branches using LLM analysis, while optimizing for token efficiency and reliability.

## Architecture Strategy

### Core Workflow
1. **PR merged to release branch** → triggers GitHub Actions
2. **Python script** sends PR diff + doc summaries to LLM
3. **LLM analysis** identifies pages needing updates
4. **Auto-create documentation PR** with findings/suggestions
5. **Human review & update** docs in the PR
6. **Merge docs PR** → sync to Confluence

### Token Optimization Approach
- **Two-phase LLM calls**: 
  - Phase A: Send PR diff + doc titles/intros for triage
  - Phase B: Send full content only for flagged pages
- **Text-based replacements**: Use before/after text chunks instead of line numbers
- **GitHub as source of truth**: Store docs in markdown, sync to Confluence
- **Future optimization**: Embedding-based similarity search for pre-filtering

## Implementation Phases

### Phase 1: Detection & Flagging Only
**Goal:** Build confidence in LLM's ability to identify relevant documentation changes

**Features:**
- Send PR diff + doc page titles/intros to LLM
- LLM returns: list of pages that might need updates + reasoning
- Create GitHub PR with analysis findings
- Human reviews flagged pages manually
- No auto-editing yet

**Files to create:**
- `doc_analyzer.py` - Main script handling workflow
- `llm_client.py` - LLM API calls (Claude/OpenAI)
- `github_helper.py` - GitHub API interactions
- `config.py` - Configuration and API keys
- `requirements.txt` - Python dependencies
- `.github/workflows/doc-analysis.yml` - GitHub Actions workflow
- `prompts.py` - LLM prompt templates
- `test_analyzer.py` - Basic tests
- `README.md` - Setup and usage instructions

**Output:** GitHub PR with structured analysis like:
```markdown
## Documentation Analysis Results

Based on code changes in PR #123, the following documentation pages may need updates:

### High Confidence
- `docs/authentication.md` - Added JWT token validation requires auth guide updates
- `docs/api-security.md` - New security patterns should be documented

### Medium Confidence  
- `docs/getting-started.md` - Auth flow examples may need refresh

### LLM Reasoning
The changes introduce JWT token validation in `auth.py` which impacts how users authenticate...

---
**This is an automated analysis. Please review and manually update the flagged documentation files.**
```

### Phase 2: Add Change Suggestions
**Goal:** Test LLM's ability to suggest specific changes

**Features:**
- For flagged pages, send full markdown content to LLM
- LLM returns: specific change suggestions using before/after text chunks
- Still requires human approval before any changes
- Creates GitHub PR with both analysis AND suggested changes

**Example LLM output format:**
```json
{
  "changes": [
    {
      "action": "replace",
      "find": "## API Authentication\n\nCurrently supports basic auth only.",
      "replace": "## API Authentication\n\nSupports basic auth and OAuth 2.0. For OAuth setup:\n\n1. Register your app\n2. Get client credentials\n3. Use authorization flow"
    },
    {
      "action": "insert_after",
      "find": "### Rate Limits\n\nAPI calls are limited to 1000/hour.",
      "insert": "\n\n### Error Handling\n\nAll errors return standard HTTP codes with JSON responses."
    }
  ]
}
```

### Phase 3: Controlled Auto-Updates
**Goal:** Automate simple, low-risk changes

**Features:**
- Add confidence scoring to LLM responses
- Auto-apply only high-confidence changes (maybe just additions, not deletions)
- Everything else still goes to human review
- All changes create PRs for review, never direct commits

**Safety mechanisms:**
- Only auto-apply changes with >90% confidence
- Never auto-delete content, only add or modify
- All changes logged and reversible

### Phase 4: Full Automation (Future)
**Goal:** Minimize human intervention for routine updates

**Features:**
- Most changes auto-applied based on confidence scores
- Only edge cases require human review
- Add embedding-based filtering for better page selection
- Advanced change validation

## Key Safety Features (All Phases)

- **Dry-run mode** for testing without making changes
- **Detailed logging** of all LLM decisions and reasoning
- **Rollback mechanism** for bad changes
- **Human override** always available
- **Gradual confidence building** - start with obvious cases
- **Text-based replacements** instead of brittle line numbers

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
- Accuracy of page flagging (precision/recall)
- Time saved in manual doc review
- False positive rate

**Phase 2:**
- Quality of suggested changes
- Acceptance rate of LLM suggestions
- Reduction in doc debt

**Phase 3+:**
- Percentage of changes auto-applied successfully
- Time from code change to doc update
- Overall documentation freshness

## Getting Started

1. **Set up Phase 1** with basic detection and flagging
2. **Validate LLM accuracy** on your specific codebase
3. **Iterate on prompts** based on false positives/negatives
4. **Gradually add automation** as confidence builds
5. **Monitor and adjust** based on team feedback

Remember: Start conservative, build confidence, then automate incrementally.