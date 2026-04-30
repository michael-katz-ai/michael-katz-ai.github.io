# Publications JSON System Guide

## Overview

The publications page now uses a **JSON-based data structure** instead of hardcoded HTML. This makes the publication list:

- ✅ **Maintainable** - Easy to add/update publications
- ✅ **Reusable** - Same data can power multiple views
- ✅ **Searchable** - Better filtering and search capabilities
- ✅ **Scalable** - Easy to add new fields or metadata
- ✅ **Topic-organized** - Publications grouped by research topics

## File Structure

```
new-site/
├── data/
│   └── publications.json          # All publication data
├── js/
│   ├── main.js                    # General site functionality
│   └── publications.js            # Publications-specific logic
└── publications.html              # Publications page (minimal HTML)
```

## JSON Schema

### Top-Level Structure

```json
{
  "metadata": {
    "lastUpdated": "YYYY-MM-DD",
    "totalPublications": 100,
    "description": "..."
  },
  "thesis": { ... },
  "topics": [ ... ]
}
```

### Thesis Object

```json
{
  "title": "Thesis Title",
  "author": "Author Name",
  "institution": "Institution Name",
  "year": 2010,
  "award": "Award Name (optional)",
  "links": {
    "pdf": "path/to/thesis.pdf",
    "slides": "path/to/slides.pdf"
  }
}
```

### Topic Structure

```json
{
  "id": "unique-topic-id",
  "name": "Topic Display Name",
  "description": "Brief description of the topic",
  "subtopics": [
    {
      "id": "unique-subtopic-id",
      "name": "Subtopic Display Name",
      "papers": [ ... ]
    }
  ]
}
```

### Paper Object

```json
{
  "id": "unique-paper-id",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2", "Author 3"],
  "venue": "ICAPS",
  "venueFullName": "International Conference on Automated Planning and Scheduling",
  "location": "City, Country",
  "year": 2024,
  "type": "conference|journal|workshop",
  "award": "Award Name (optional)",
  "volume": 32,              // For journals
  "pages": "203-288",        // For journals
  "links": {
    "pdf": "path/to/paper.pdf",
    "slides": "path/to/slides.pdf",
    "code": "https://github.com/...",
    "video": "https://youtube.com/..."
  },
  "tags": ["tag1", "tag2", "tag3"]
}
```

## Adding a New Publication

### Step 1: Identify the Topic and Subtopic

Find the appropriate topic in `data/publications.json`. Topics are:

1. **LLMs for Planning and Neuro-Symbolic Reasoning**
   - Position Papers
   - Thought of Search
   - NL2PDDL
   - NL2Policy
   - Benchmarking and Fine-tuning

2. **Multiple Solutions for Classical Planning**
   - Top-k/Top-quality Planning
   - Diverse Planning

3. **Theory and Practice of Classical Planning**
   - Abstractions
   - Cost Partitioning
   - Partial Satisfaction Planning
   - Red-Black Planning
   - Planner Selection
   - State Pruning Techniques
   - Novelty

4. **Planning and Reinforcement Learning**
   - Planning annotated RL (PaRL)
   - Action Models & Rewards

5. **Applications, Data, and AI Planning based solutions**
   - IBM Scenario Planning Advisor
   - Data
   - Other Applications

### Step 2: Add the Paper Object

Add your paper to the appropriate `papers` array:

```json
{
  "id": "venue2025-shortname",
  "title": "Your Paper Title",
  "authors": ["First Author", "Second Author", "M. Katz"],
  "venue": "ICAPS",
  "venueFullName": "Proceedings of The 35th International Conference on Automated Planning and Scheduling",
  "location": "City, Country",
  "year": 2025,
  "type": "conference",
  "links": {
    "pdf": "../papers/icaps2025.pdf"
  },
  "tags": ["planning", "heuristics"]
}
```

### Step 3: Update Metadata

Update the `lastUpdated` date and `totalPublications` count in the metadata section.

### Step 4: Test

Open `publications.html` in a browser and verify:
- ✅ Paper appears in the correct topic/subtopic
- ✅ All links work
- ✅ Search finds the paper
- ✅ Filtering works correctly

## Features

### 1. Topic-Based Organization

Publications are organized by research topics with collapsible sections:
- Click topic header to expand/collapse
- Use "Expand All" / "Collapse All" buttons for bulk operations

### 2. Search Functionality

Search across:
- Paper titles
- Author names
- Venue names

The search is case-insensitive and updates results in real-time.

### 3. Type Filtering

Filter publications by type:
- All
- Conferences
- Journals
- Workshops

### 4. Award Highlighting

Papers with awards are automatically highlighted with:
- Amber border
- Award badge with trophy emoji
- Special styling

### 5. Dynamic Statistics

The footer automatically updates to show the correct number of publications.

## JavaScript API

The `PublicationsManager` class provides these methods:

```javascript
// Initialize the system
await pubManager.init();

// Load data
await pubManager.loadData();

// Render components
pubManager.renderThesis();
pubManager.renderTopics();

// Filter publications
pubManager.filterPublications();

// Toggle all topics
pubManager.toggleAllTopics(collapse);
```

## Styling

Topic-specific styles are defined in `publications.html`:

- `.topic-section` - Container for each topic
- `.topic-header` - Clickable header with gradient
- `.topic-content` - Collapsible content area
- `.subtopic-section` - Container for subtopics
- `.publication-item` - Individual paper card

## Best Practices

### 1. Consistent IDs

Use descriptive, unique IDs:
- Format: `venue-year-shortname`
- Example: `icaps2024-topk-planning`

### 2. Author Names

- Use consistent formatting (e.g., "M. Katz" not "Michael Katz")
- Maintain order as in the paper
- Use full names for first/last authors when appropriate

### 3. Venue Names

- Use standard abbreviations (ICAPS, AAAI, IJCAI, etc.)
- Include full name in `venueFullName`
- Include location for conferences

### 4. Links

- Use relative paths for local PDFs: `../papers/filename.pdf`
- Use absolute URLs for external resources
- Always include at least a PDF link

### 5. Tags

- Use lowercase, hyphenated tags
- Be consistent across papers
- Common tags: `planning`, `heuristics`, `llm`, `reinforcement-learning`, etc.

## Migration from Old System

The old year-based system has been replaced with topic-based organization. To migrate:

1. **Identify the topic** for each paper
2. **Extract paper details** from HTML
3. **Create JSON object** following the schema
4. **Add to appropriate subtopic** in `publications.json`
5. **Verify** the paper appears correctly

## Troubleshooting

### Publications not appearing

1. Check browser console for errors
2. Verify JSON syntax is valid (use a JSON validator)
3. Ensure `publications.js` is loaded after `main.js`
4. Check that paper has `papers` array (not empty)

### Search not working

1. Verify search input has `id="pub-search"`
2. Check that publication items have correct classes
3. Ensure JavaScript is enabled

### Topics not collapsing

1. Check that topic headers have correct class
2. Verify event listeners are attached
3. Check browser console for JavaScript errors

## Future Enhancements

Potential improvements:

- [ ] Add year-based view toggle
- [ ] Export to BibTeX
- [ ] Citation count integration
- [ ] Advanced filtering (by year range, co-authors, etc.)
- [ ] Publication timeline visualization
- [ ] Related papers suggestions
- [ ] PDF preview on hover

## Support

For issues or questions:
1. Check this guide
2. Review `publications.js` comments
3. Inspect browser console for errors
4. Validate JSON at jsonlint.com