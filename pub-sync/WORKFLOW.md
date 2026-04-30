# Publication Synchronization Workflow

## Overview

This toolkit maintains publication data consistency across three sources:
1. **BibTeX database** (authoritative for metadata)
2. **CV LaTeX file** (authoritative for categories)
3. **Website JSON** (generated from merged data)

## Complete Workflow

### 1. Extract Publications from BibTeX

```bash
# Extract all Michael Katz publications from BibTeX
python3 bibtex_to_jsonl.py \
  ../../papers/references.bib \
  katz_publications.jsonl \
  --author "Michael Katz" \
  --exclude misc
```

**Output:** `katz_publications.jsonl` (111 publications)
- Contains complete BibTeX metadata
- Excludes Zenodo entries (misc type)
- Filtered to Michael Katz as author

### 2. Extract Publications from CV

```bash
# Extract publications with categories from CV
python3 cv_to_jsonl_v2.py \
  ../../CV_Michael_Katz.tex \
  cv_with_categories_v2.jsonl
```

**Output:** `cv_with_categories_v2.jsonl` (95 publications)
- Contains titles and categories
- Preserves CV organization structure
- 5 main categories with subcategories

### 3. Merge BibTeX and CV Data

```bash
# Create unified JSONL with BibTeX metadata + CV categories
python3 merge_bibtex_cv.py \
  katz_publications.jsonl \
  cv_with_categories_v2.jsonl \
  katz_unified.jsonl \
  --author "Michael Katz"
```

**Output:** `katz_unified.jsonl` (111 publications)
- BibTeX metadata (authoritative)
- CV categories where titles match (85/111)
- 26 uncategorized (newer papers not in CV)

**Match Statistics:**
- Matched with CV: 85 publications
- No CV match: 26 publications
- Total: 111 publications

**Category Distribution:**
- Theory and Practice of Classical Planning: 43
- Applications, Data, and AI Planning: 13
- LLMs for Planning and Neuro-Symbolic Reasoning: 13
- Multiple Solutions for Classical Planning: 10
- Planning and Reinforcement Learning: 6
- Uncategorized: 26

### 4. Generate Website JSON

```bash
# Convert unified JSONL to website-ready JSON
python3 format_website_json.py \
  katz_unified.jsonl \
  publications.json
```

**Output:** `publications.json`
- Organized by category
- Sorted by year (descending) within categories
- Includes PDF links
- Ready for website integration

**JSON Structure:**
```json
{
  "categories": {
    "Category Name": {
      "count": 13,
      "publications": [
        {
          "id": "bibtex-key",
          "title": "Paper Title",
          "authors": ["Author 1", "Author 2"],
          "year": "2024",
          "venue": "Conference Name",
          "pdf": "papers/bibtex-key.pdf",
          "category": "Category Name",
          "subcategory": "Subcategory Name"
        }
      ]
    }
  },
  "total_publications": 111,
  "last_updated": "2026-04-29"
}
```

## Alternative Outputs

### Generate BibTeX File

```bash
python3 format_publications.py \
  katz_unified.jsonl \
  katz_publications.bib \
  --format bibtex
```

### Generate CV LaTeX

```bash
python3 format_publications.py \
  katz_unified.jsonl \
  katz_publications_cv.tex \
  --format cv
```

### Generate Website JSON (Alternative)

```bash
python3 format_publications.py \
  katz_unified.jsonl \
  katz_publications_web.json \
  --format website
```

## Maintenance Tasks

### Adding New Publications

1. Add to BibTeX database (`papers/references.bib`)
2. Re-run extraction: `python3 bibtex_to_jsonl.py ...`
3. Optionally add to CV with category
4. Re-run merge: `python3 merge_bibtex_cv.py ...`
5. Re-generate website JSON: `python3 format_website_json.py ...`

### Updating Categories

1. Update CV LaTeX file with new categories
2. Re-run CV extraction: `python3 cv_to_jsonl_v2.py ...`
3. Re-run merge: `python3 merge_bibtex_cv.py ...`
4. Re-generate website JSON: `python3 format_website_json.py ...`

### Fixing Metadata

1. Update BibTeX database (authoritative source)
2. Re-run entire workflow from step 1

## Data Flow

```
BibTeX Database (references.bib)
    ↓ [bibtex_to_jsonl.py]
katz_publications.jsonl (111 pubs, metadata only)
    ↓
    ↓ [merge_bibtex_cv.py]
    ↓                           CV LaTeX (CV_Michael_Katz.tex)
    ↓                               ↓ [cv_to_jsonl_v2.py]
    ↓                           cv_with_categories_v2.jsonl (95 pubs, categories only)
    ↓                               ↓
katz_unified.jsonl (111 pubs, metadata + categories)
    ↓ [format_website_json.py]
publications.json (website-ready)
```

## File Descriptions

### Input Files
- `../../papers/references.bib` - Master BibTeX database (2,267 entries)
- `../../CV_Michael_Katz.tex` - CV with categorized publications (95 entries)

### Intermediate Files
- `katz_publications.jsonl` - BibTeX data for Michael Katz (111 entries)
- `cv_with_categories_v2.jsonl` - CV data with categories (95 entries)
- `katz_unified.jsonl` - Merged data (111 entries with categories)

### Output Files
- `publications.json` - Website-ready JSON (111 entries, organized by category)

### Tools
- `bibtex_to_jsonl.py` - BibTeX → JSONL converter
- `cv_to_jsonl_v2.py` - CV LaTeX → JSONL extractor
- `merge_bibtex_cv.py` - Merge BibTeX + CV data
- `format_website_json.py` - JSONL → Website JSON
- `format_publications.py` - JSONL → BibTeX/CV/Web (alternative)

## Quality Checks

### Verify Counts
```bash
# Count publications in each file
wc -l katz_publications.jsonl      # Should be 111
wc -l cv_with_categories_v2.jsonl  # Should be 95
wc -l katz_unified.jsonl           # Should be 111
```

### Check Categories
```bash
# Show category distribution
python3 merge_bibtex_cv.py \
  katz_publications.jsonl \
  cv_with_categories_v2.jsonl \
  /dev/null \
  --author "Michael Katz"
```

### Validate JSON
```bash
# Check JSON syntax
python3 -m json.tool publications.json > /dev/null && echo "Valid JSON"
```

## Notes

- **Title Matching:** Uses normalized titles (lowercase, no punctuation, LaTeX stripped)
- **Author Filtering:** Case-insensitive substring matching
- **Year Handling:** Converts to string for consistency
- **PDF Links:** Generated from BibTeX keys (assumes `papers/{key}.pdf`)
- **Subcategories:** Extracted but may need manual cleanup
- **Uncategorized Papers:** Newer papers not yet in CV (26 papers)

## Future Enhancements

- [ ] Improve subcategory extraction accuracy
- [ ] Add automated CV category assignment for new papers
- [ ] Create web interface for category management
- [ ] Add duplicate detection across sources
- [ ] Implement automated consistency checking
- [ ] Generate publication statistics and visualizations