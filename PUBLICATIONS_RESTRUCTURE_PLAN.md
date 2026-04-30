# Publications Page Restructuring Plan

## Current Status (Updated 2026-04-29)

### Publication Extraction Complete ✅
- **Total Publications:** 110 (after deduplication)
- **Categorized:** 86 publications
- **Uncategorized:** 24 publications
- **Source:** BibTeX (117 entries) merged with CV LaTeX (95 entries)

### Data Pipeline
1. **BibTeX Extraction** (`bibtex_to_jsonl.py`)
   - Extracts from `literatur.bib` with crossref resolution
   - Filters out Zenodo entries (checks `howpublished` field)
   - Includes arXiv preprints and other @Misc entries
   - Output: `katz_publications.jsonl` (117 entries)

2. **CV Extraction** (`cv_to_jsonl_v2.py`)
   - Extracts from `chatgpt-cv.tex` with categories and subcategories
   - Output: `katz_cv_publications.jsonl` (95 entries)

3. **Merge** (`merge_bibtex_cv.py`)
   - Merges BibTeX metadata with CV categories
   - Output: `katz_unified.jsonl` (117 entries)

4. **Deduplication** (`deduplicate_publications.py`)
   - Removes duplicates, prioritizing: Journal > Conference > Workshop > Tech Report
   - Output: `katz_unified_deduplicated.jsonl` (110 entries)

5. **Website Format** (`format_website_json_v2.py`)
   - Filters to categorized publications only
   - Uses `topic_order.json` and `paper_order.json` for ordering
   - Output: `../data/publications.json` (86 entries)

## Topic Categories (from CV LaTeX)

### 1. LLMs for Planning and Neuro-Symbolic Reasoning (14 papers)
**Subtopics:**
- Position (1 paper) - includes arXiv 2025 "Make Planning Research Rigorous Again!"
- Thought of Search (3 papers)
- NL2PDDL (3 papers)
- NL2Policy (2 papers)
- Benchmarking and Fine-tuning (5 papers)

### 2. Multiple Solutions for Classical Planning (11 papers)
**Subtopics:**
- Top-k/Top-quality Planning (8 papers)
- Diverse Planning (3 papers)

### 3. Theory and Practice of Classical Planning (42 papers)
**Subtopics:**
- Abstractions (9 papers)
- Cost Partitioning (3 papers)
- Partial Satisfaction Planning (6 papers)
- Red-Black Planning (6 papers)
- Planner Selection (3 papers)
- State Pruning Techniques (11 papers)
- Novelty (4 papers)

### 4. Planning and Reinforcement Learning (7 papers)
**Subtopics:**
- Planning annotated RL (PaRL) (3 papers)
- Action Models & Rewards (4 papers)

### 5. Applications, Data, and AI Planning based solutions (12 papers)
**Subtopics:**
- IBM Scenario Planning Advisor (5 papers)
- Data (4 papers)
- Other Applications (3 papers)

## Uncategorized Publications (24 entries)

### IPC/Competition Entries (11)
- **Hapori variants (2023):** Delfi, Explainable DT, Explainable LR, Greedy, IBaCoP2, MIPlan, Stone Soup
- **2018:** Cerberus, Delfi, MERWIN, Metis 2018
- **2014:** Mercury Planner, Metis

### Workshop Papers (5)
- Reshaping Diverse Planning (2019)
- Top-Quality: Finding Practically Useful Sets of Best Plans (2019)
- Structural Symmetries of the Lifted Representation (2017)
- Abstractions += Landmarks (2009)
- Structural Patterns Heuristics (2007)

### Tech Reports (3)
- Red-Black Heuristic with Conditional Effects (2019)
- Symmetry Breaking in Deterministic Planning (2015)
- Heuristics and Symmetries: Additional Proofs (2014)

### System Demos (2)
- Planutils: Bringing Planning to the Masses (2022)
- Mercury Planner (2014)

### Other (3)
- General Agent Evaluation (2026 arXiv) - `bandel-et-al-arxiv2026`
- Adaptive Planner Scheduling with GNNs (2018) - `ma-et-al-corr2018`

## Recent Changes

### 2026-04-29: Fixed Missing arXiv Paper
- **Issue:** `katz-et-al-arxiv2025a` was missing from publications
- **Cause:** Script was filtering out all `@Misc` entries (including arXiv preprints)
- **Fix:** Modified `bibtex_to_jsonl.py` to only filter Zenodo entries (checks `howpublished` field for "zenodo")
- **Result:** arXiv paper now included in "LLMs for Planning" → "Position" subcategory

### Configuration Files
- `topic_order.json` - Controls display order of topics and subtopics
- `paper_order.json` - Controls display order of individual papers within subtopics (by BibTeX key)

## Implementation Strategy

✅ **Completed:**
1. Created JSON-based publication data structure
2. Implemented topic-based organization matching CV
3. Added collapsible sections for topics and subtopics
4. Maintained search functionality across all topics
5. Created automated extraction pipeline from BibTeX and CV
6. Added configuration-based ordering system

## Key Features
- Topic-based organization (not year-based)
- Collapsible sections for topics and subtopics
- Search functionality across all publications
- PhD thesis highlight section
- Award highlights (ICAPS 2008 influential paper, etc.)
- Automated extraction and synchronization with BibTeX and CV
- Manual ordering control via JSON configuration files