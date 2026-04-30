# Uncategorized Publications Review - RESOLVED

**Date:** 2026-04-29
**Status:** ✅ All uncategorized publications have been resolved

---

## Summary

Out of 110 publications in the deduplicated dataset:
- **Categorized and included:** 103 publications
- **Excluded:** 7 publications
- **Remaining uncategorized:** 0 publications

### Verification
```bash
$ python3 list_uncategorized.py katz_unified_categorized.jsonl
Found 0 uncategorized publications:
```

All publications in the final dataset (`katz_unified_categorized.jsonl`) have been properly categorized.

### Note on katz-aaai2019
This paper was initially listed as a `@TechReport` in the BibTeX file and was excluded. After the BibTeX entry was updated to `@InProceedings`, it was re-extracted and categorized under "Theory and Practice of Classical Planning" → "Red-Black Planning". The deduplication process correctly kept the 2019 AAAI conference paper and removed the 2018 IBM technical report version.

### Breakdown by Action

#### 1. Added to Website (17 publications)
These were previously uncategorized and have now been properly categorized:

**IPC Planners (11)** → Applications, Data, and AI Planning based solutions / IPC Planners
- ferber-et-al-ipc2023a - Hapori Delfi
- ferber-et-al-ipc2023b - Hapori Explainable Decision Tree
- ferber-et-al-ipc2023c - Hapori Explainable Linear Regression
- ferber-et-al-ipc2023d - Hapori Greedy
- ferber-et-al-ipc2023e - Hapori IBaCoP2
- ferber-et-al-ipc2023f - Hapori MIPlan
- ferber-et-al-ipc2023g - Hapori Stone Soup
- katz-ipc2018 - Cerberus
- katz-et-al-ipc2018 - Delfi
- katz-et-al-ipc2018b - MERWIN Planner
- sievers-katz-ipc2018 - Metis 2018

**Data & Tools (1)** → Applications, Data, and AI Planning based solutions / Data & Tools
- muise-et-al-icaps2022systemdemos - Planutils: Bringing Planning to the Masses

**Theory and Practice (5)**
- domshlak-et-al-tr2015 → State Pruning Techniques (Tech report)
- ma-et-al-corr2018 → Planner Selection (ArXiv)
- katz-hoffmann-ipc2014 → Partial Satisfaction Planning (Mercury Planner)
- alkhazraji-et-al-ipc2014 → Red-Black Planning (Metis)
- katz-aaai2019 → Red-Black Planning (AAAI 2019 conference paper)

#### 2. Excluded (7 publications)

**Tech Reports - Not Important (1)**
- shleyfman-et-al-tr2014 - Heuristics and Symmetries in Classical Planning: Additional Proofs

**Not Authored by Michael Katz (1)**
- bandel-et-al-arxiv2026 - General Agent Evaluation (has "Yoav Katz", not "Michael Katz")

**Workshop Papers Superseded by Conference Publications (5)**
- katz-domshlak-icaps2007wshdip - Structural Patterns Heuristics: Basic Idea and Concrete Instance
- domshlak-et-al-icaps2009wshdip - Abstractions += Landmarks
- sievers-et-al-icaps2017wshsdip-a - Structural Symmetries of the Lifted Representation
- katz-sohrabi-icaps2019wshsdip - Reshaping Diverse Planning: Let There Be Light!
- katz-et-al-icaps2019wshsdip - Top-Quality: Finding Practically Useful Sets of Best Plans

---

## Final Publication Counts

### By Topic
- **LLMs for Planning and Neuro-Symbolic Reasoning:** 14 publications
- **Multiple Solutions for Classical Planning:** 11 publications (down from 13, excluded 2 workshop papers)
- **Theory and Practice of Classical Planning:** 47 publications (includes katz-aaai2019)
- **Planning and Reinforcement Learning:** 7 publications
- **Applications, Data, and AI Planning based solutions:** 24 publications (11 IPC planners + tools)

### By Subcategory (Applications)
- **IBM Scenario Planning Advisor:** 5 publications
- **Data & Tools:** 5 publications (includes Planutils)
- **IPC Planners:** 11 publications (NEW subcategory)
- **Other Applications:** 3 publications

**Total:** 103 publications on website

---

## Configuration Files

### uncategorized_resolution.json
Contains the mapping of uncategorized publications to their proper categories or exclusion list.

**Structure:**
```json
{
  "add_to_cv": {
    "Category Name": {
      "Subcategory Name": ["paper-id-1", "paper-id-2", ...]
    }
  },
  "exclude": {
    "papers": [
      {"id": "paper-id", "reason": "explanation"}
    ]
  }
}
```

### apply_uncategorized_resolution.py
Script that reads the resolution config and applies categorizations to the JSONL data.

**Usage:**
```bash
python3 apply_uncategorized_resolution.py input.jsonl resolution.json output.jsonl
```

---

## Notes

1. **IPC Planners subcategory** was created to house competition entries that are system descriptions rather than research papers.

2. **Workshop papers** that were superseded by conference publications are excluded to avoid duplication and maintain focus on the most complete versions.

3. **Data subcategory renamed to "Data & Tools"** to better reflect its content (datasets and software tools).

4. **Mercury and Metis (2014)** were correctly categorized as research papers (Partial Satisfaction Planning and Red-Black Planning) rather than just IPC entries, as they contain significant research contributions.

5. The **ma-et-al-corr2018** ArXiv paper on adaptive planner scheduling was included as it's relevant to planner selection research.

---

## Resolution Complete ✅

All uncategorized publications have been reviewed and either:
- Properly categorized and added to the website (16 publications)
- Excluded with documented reasons (8 publications)

The website now displays 102 well-organized publications across 5 major research topics.