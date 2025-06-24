# AI Documentation Assistant

An intelligent GitHub Actions-powered system that automatically generates and maintains wiki documentation for data-related code changes in your repository.

## 🎯 Overview

The AI Documentation Assistant is a sophisticated automation tool that:

- **Analyzes** your existing GitHub wiki to understand current documentation
- **Detects** new data-related changes in pull requests using AI
- **Intelligently decides** whether new documentation is needed
- **Automatically updates** the appropriate wiki pages with contextually relevant content

Unlike traditional documentation generators that create redundant content, this system uses AI to understand your existing documentation patterns and only creates or updates documentation for genuinely new concepts.

## ✨ Key Features

### 🧠 Intelligent Analysis
- Scans existing wiki structure and content
- Uses AI to compare PR changes against documented features
- Identifies gaps in documentation coverage
- Makes context-aware decisions about documentation needs

### 🎯 Smart Documentation Strategy
- **Create New Page**: For completely new features or data domains
- **Update Existing Page**: For additions to documented areas
- **Append to Page**: For related but separate additions
- **Update Multiple Pages**: For cross-cutting changes

### 📊 Data-Focused Detection
Automatically detects and documents:
- Database schema changes (tables, columns, indexes)
- API endpoint modifications and new response formats
- Data transformation and business logic changes
- Configuration updates affecting data flow
- Migration scripts and data cleanup operations

### 🔄 Maintenance-Free Operation
- Runs automatically on PR merges via GitHub Actions
- Maintains consistent documentation structure
- Prevents documentation drift and redundancy
- Integrates seamlessly with existing workflows

## 🚀 Quick Start

### Prerequisites
- GitHub repository with wiki enabled
- Python 3.7+ environment
- AI API access (OpenAI or Anthropic)

### 1. Setup Secrets
Add these secrets to your GitHub repository:

```bash
# Required: AI API Key
AI_API_KEY=your_anthropic_or_openai_api_key

# Auto-configured: GitHub token (automatically available)
GITHUB_TOKEN=automatically_provided_by_github
```

### 2. Add Workflow File
Create `.github/workflows/ai-documentation.yml`:

```yaml
name: AI Documentation Generator

on:
  push:
    branches: [ main, master ]
  pull_request:
    types: [closed]
    branches: [ main, master ]

jobs:
  generate-documentation:
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.pull_request.merged == true)
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests
        
    - name: Generate AI Documentation
      env:
        AI_API_KEY: ${{ secrets.AI_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        python scripts/ai_doc_generator.py \
          --commit-sha ${{ github.sha }} \
          --ai-provider anthropic
```

### 3. Add the Script
Copy the `ai_doc_generator.py` script to your `scripts/` directory.

### 4. Test Run
Make a data-related change and push to trigger the workflow!

## 📖 How It Works

### Phase 1: Wiki Analysis
```
📋 Analyzing existing wiki...
   ├── Found 5 existing pages
   ├── Database Schema (2,340 chars) - Contains schema content
   ├── API Documentation (1,820 chars) - Contains API content
   └── Data Flow (980 chars) - Contains data flow content
```

### Phase 2: Change Detection
```
🔍 Analyzing commit changes...
   ├── Files: schema.sql, UserService.java, api.yaml
   ├── Detected: New 'subtitle' column in posts table
   └── AI Assessment: NEW data concept requiring documentation
```

### Phase 3: Strategy Selection
```json
{
  "needs_documentation": true,
  "reasoning": "New subtitle column introduces data concept not covered in existing schema docs",
  "documentation_strategy": {
    "action": "update_existing_page",
    "target_pages": ["Database Schema"],
    "content_type": "schema"
  }
}
```

### Phase 4: Intelligent Execution
```
📝 Updating documentation...
   ├── Strategy: update_existing_page
   ├── Target: Database Schema
   ├── AI merging new content into existing structure
   └── ✅ Successfully updated: https://github.com/user/repo/wiki/Database-Schema
```

## 🛠️ Configuration Options

### Command Line Usage

```bash
# Basic usage
python scripts/ai_doc_generator.py --commit-sha abc123

# Specify AI provider
python scripts/ai_doc_generator.py --commit-sha abc123 --ai-provider openai

# Dry run (preview without updating)
python scripts/ai_doc_generator.py --commit-sha abc123 --dry-run

# Manual repo specification
python scripts/ai_doc_generator.py --commit-sha abc123 --repo-owner mycompany --repo-name myapp
```

### AI Provider Options

**Anthropic (Recommended)**
```bash
export AI_API_KEY=your_anthropic_key
python scripts/ai_doc_generator.py --commit-sha abc123 --ai-provider anthropic
```

**OpenAI**
```bash
export AI_API_KEY=your_openai_key
python scripts/ai_doc_generator.py --commit-sha abc123 --ai-provider openai
```

## 📋 Documentation Examples

### Example 1: New Database Table
**Code Change:**
```sql
CREATE TABLE user_preferences (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    theme VARCHAR(20) DEFAULT 'light',
    notifications BOOLEAN DEFAULT true
);
```

**AI Decision:** "New table not documented - CREATE new page"

**Generated Documentation:**
```markdown
# User Preferences Schema

**Created:** 2024-06-24
**Content Type:** schema

## Database Schema Changes

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | BIGINT | PRIMARY KEY | Unique identifier |
| user_id | BIGINT | FOREIGN KEY | References users table |
| theme | VARCHAR(20) | DEFAULT 'light' | UI theme preference |
| notifications | BOOLEAN | DEFAULT true | Email notification setting |

## Business Context
This table stores user-specific preferences for UI customization and notification settings...
```

### Example 2: API Endpoint Addition
**Code Change:**
```java
@GetMapping("/api/posts/{id}/comments")
public ResponseEntity<List<Comment>> getPostComments(@PathVariable Long id) {
    return ResponseEntity.ok(commentService.getCommentsByPostId(id));
}
```

**AI Decision:** "New endpoint for existing API - APPEND to API page"

**Generated Documentation:**
```markdown
## Update 2024-06-24 - New Comment Retrieval Endpoint

### GET /api/posts/{id}/comments

Retrieves all comments for a specific post.

**Parameters:**
- `id` (path): Post ID

**Response:**
```json
[
  {
    "id": 1,
    "postId": 123,
    "content": "Great post!",
    "authorId": 456
  }
]
```

## 🔧 Architecture

### Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  GitHub Actions │────│ AI Doc Generator │────│   GitHub Wiki   │
│                 │    │                  │    │                 │
│ • Trigger       │    │ • Git Analysis   │    │ • Page Updates  │
│ • Environment   │    │ • AI Processing  │    │ • Version Control│
│ • Secrets       │    │ • Wiki Management│    │ • Public Access │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AI Provider    │
                       │                  │
                       │ • OpenAI GPT-4   │
                       │ • Anthropic      │
                       │   Claude         │
                       └──────────────────┘
```

### Key Classes

**`GitHubWikiAPI`**
- Manages wiki repository operations
- Clones, analyzes, and updates wiki content
- Handles git authentication and operations

**`AIDocumentationGenerator`**
- Processes git changes and diffs
- Communicates with AI providers
- Generates documentation content

**Core Methods:**
- `analyze_wiki_structure()` - Scans existing documentation
- `intelligent_documentation_strategy()` - AI-powered decision making
- `execute_intelligent_documentation()` - Updates wiki pages

## 🎯 Use Cases

### Enterprise Development Teams
- **Problem**: Manual documentation maintenance is time-consuming and often skipped
- **Solution**: Automatic documentation generation for all data-related changes
- **Benefit**: Always up-to-date data governance documentation

### API Development
- **Problem**: API documentation becomes stale as endpoints evolve
- **Solution**: Intelligent detection and documentation of API changes
- **Benefit**: Accurate API documentation for consumers

### Database Evolution
- **Problem**: Schema changes lack proper documentation for future reference
- **Solution**: Automatic schema change documentation with business context
- **Benefit**: Clear audit trail of database evolution

### Open Source Projects
- **Problem**: Contributors don't always update documentation
- **Solution**: AI assistant ensures documentation completeness
- **Benefit**: Better project maintainability and contributor onboarding

## 🚨 Troubleshooting

### Common Issues

**❌ "Error parsing AI strategy response"**
- **Cause**: AI returned malformed JSON
- **Solution**: Fixed in latest version with improved JSON parsing
- **Action**: Update to latest script version

**❌ "Failed to clone wiki repository"**
- **Cause**: Wiki not initialized or permissions issue
- **Solution**: Initialize wiki with at least one page
- **Action**: Create a "Home" page in your GitHub wiki

**❌ "AI determined no documentation needed"**
- **Cause**: Changes don't contain new data concepts
- **Solution**: This is often correct - AI detected changes are already documented
- **Action**: Review logs to confirm AI reasoning

**❌ "Missing GITHUB_TOKEN"**
- **Cause**: Token not available in environment
- **Solution**: Ensure workflow has proper permissions
- **Action**: Add `contents: read` and `pages: write` to workflow

### Debug Mode

Enable detailed logging:
```bash
export DEBUG=1
python scripts/ai_doc_generator.py --commit-sha abc123 --dry-run
```

### Manual Override

Force documentation generation:
```bash
# Bypass intelligent analysis
python scripts/ai_doc_generator.py --commit-sha abc123 --force-documentation
```

## 🔮 Advanced Features

### Custom Documentation Templates
Modify the AI prompts in `ai_doc_generator.py` to match your organization's documentation standards.

### Multi-Repository Support
Run the assistant across multiple repositories with shared wiki documentation.

### Integration Analytics
Track documentation coverage and quality metrics over time.

### Custom Rules Engine
Add organization-specific rules for documentation requirements.

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd AI-documentation-assistant-POC
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Tests
```bash
python -m pytest tests/
python scripts/ai_doc_generator.py --commit-sha HEAD --dry-run
```

### Code Structure
```
scripts/
├── ai_doc_generator.py      # Main application
└── requirements.txt         # Dependencies

.github/workflows/
└── ai-documentation.yml     # GitHub Actions workflow

docs/
├── README.md               # This file
├── WIKI_MANAGEMENT.md      # Detailed system documentation
└── examples/               # Usage examples
```

## 📊 Performance & Limits

### AI API Usage
- **Anthropic Claude**: ~2-3 API calls per commit
- **OpenAI GPT-4**: ~2-3 API calls per commit
- **Cost**: Typically $0.01-0.05 per documentation generation

### GitHub Rate Limits
- Uses standard GitHub API with built-in token
- No additional rate limiting concerns

### Processing Time
- Small changes: 30-60 seconds
- Large changes: 1-3 minutes
- Wiki analysis: Additional 10-30 seconds

## 📚 Documentation

- **[System Overview](./WIKI_MANAGEMENT.md)** - Detailed technical documentation
- **[GitHub Wiki](../../wiki)** - Live examples of generated documentation
- **[Workflow Examples](./.github/workflows/)** - GitHub Actions configurations

## 📄 License

MIT License - feel free to use and modify for your projects!

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Wiki Management**: [Detailed Guide](./WIKI_MANAGEMENT.md)

---

**Made with ❤️ for developers who value good documentation**