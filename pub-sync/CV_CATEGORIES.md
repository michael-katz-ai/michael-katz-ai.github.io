# CV Publication Categories and Subcategories

Extracted from CV LaTeX file: `/Users/michaelkatz/software/LaTeX/papers-old/cv/chatgpt-cv.tex`

## Current Structure (5 Main Categories, 18 Subcategories)

### 1. LLMs for Planning and Neuro-Symbolic Reasoning
- **Position** (papers about the field/position papers)
- **Thought of Search** (ToS methodology)
- **NL2PDDL** (Natural language to PDDL domain generation)
- **NL2Policy** (Natural language to policy generation)
- **Benchmarking and fine-tuning** (evaluation and improvement)

### 2. Multiple Solutions for Classical Planning
- **Top-k/Top-quality Planning** (finding multiple high-quality plans)
- **Diverse Planning** (finding diverse sets of plans)

### 3. Theory and Practice of Classical Planning
- **Abstractions** (abstraction-based heuristics)
- **Cost Partitioning** (cost partitioning heuristics)
- **Partially Satisfaction Planning** (oversubscription planning)
- **Red-Black Planning** (red-black heuristics)
- **Planner Selection** (online/offline planner selection)
- **State Pruning Techniques** (Symmetry & Partial Order Reduction) & Relevance Analysis
- **Novelty** (novelty-based pruning)

### 4. Planning and Reinforcement Learning
- **Action Models & Rewards** (learning models and reward functions)

### 5. Applications, Data, and AI Planning based solutions
- **Data** (datasets, benchmarks, IPC)
- **Other Applications** (enterprise applications, scenario planning, etc.)

---

## Decision: Keep Existing 5 Categories

**User Decision:** Maintain the current 5-category structure. IPC planner descriptions and system demos (like Planutils) will be added to the existing "Applications, Data, and AI Planning" category.

### Updated Category 5: Applications, Data, and AI Planning

**Existing Subcategories:**
- **Data** (datasets, benchmarks, IPC)
- **Other Applications** (enterprise applications, scenario planning, etc.)

**Proposed Additions to "Data" Subcategory:**

#### IPC Planner Descriptions (High Priority):
1. ✅ **Delfi: Online Planner Selection for Cost-Optimal Planning** (IPC 2018)
   - Winner of IPC 2018 Deterministic Sequential Optimal Track
   - Significant achievement, should be in CV

2. ⚠️ **MERWIN Planner** (IPC 2018)
   - Consider based on significance

3. ⚠️ **Cerberus** (IPC 2018)
   - Consider based on significance

4. ⚠️ **Metis** (IPC 2014, 2018)
   - Already in BibTeX, consider adding

5. ⚠️ **Mercury** (IPC 2014)
   - Runner-up in IPC 2014, consider adding

6. ⚠️ **Hapori variants** (IPC 2023) - 7 planners
   - Consider if they represent distinct contributions

#### System Demonstrations (Medium Priority):
1. ⚠️ **Planutils: Bringing Planning to the Masses** (ICAPS 2022)
   - Widely-used tool in the community
   - Consider adding to "Data" or "Other Applications"

2. ⚠️ **IBM Scenario Planning Advisor demos** (AAAI, IJCAI, ICAPS)
   - Already have journal paper, demos may be redundant

### Papers NOT to Add:

#### Workshop Papers:
- Most workshop papers represent early versions of conference papers
- Keep only conference versions in CV
- Exception: "Who Said We Need to Relax All Variables?" (2013) - appears to be main conference paper, should verify

#### Technical Reports:
- ❌ Red-Black Heuristic TR (2018) - superseded by AAAI 2019 paper
- ❌ Other TRs that duplicate published work

---

## Category Statistics

### Current Distribution (95 papers):
- LLMs for Planning: ~15-20 papers
- Multiple Solutions: ~10 papers
- Theory and Practice: ~50 papers (largest category)
- Planning and RL: ~5 papers
- Applications: ~10 papers

### Proposed Distribution (with additions):
- LLMs for Planning: ~15-20 papers
- Multiple Solutions: ~10 papers
- Theory and Practice: ~50 papers
- Planning and RL: ~5 papers
- Applications: ~10 papers
- **IPC: ~12 papers** (new)
- **Workshops/Tech Reports: ~5 papers** (new)
- **System Demos: ~3 papers** (new)

**Total with additions: ~110-115 papers**

---

## Recommendations

### High Priority Additions:

1. **Add IPC Category**
   - ✅ Delfi (Winner IPC 2018) - significant achievement
   - ⚠️ Consider other IPC planners based on significance

2. **Add Selected Workshop Papers**
   - ✅ "Who Said We Need to Relax All Variables?" (2013) - appears to be main conference
   - ✅ Top-Quality and Reshaping Diverse Planning (2019) - significant HSDIP papers
   - ⚠️ Consider other workshop papers based on impact

3. **System Demos**
   - ⚠️ Consider if demos represent significant contributions
   - Planutils is a widely-used tool

### Medium Priority:

4. **Technical Reports**
   - ⚠️ Only if they contain unique content not in published papers
   - Red-Black TR (2018) is superseded by AAAI 2019 paper - exclude

5. **Hapori Variants (IPC 2023)**
   - ⚠️ 7 variants - consider if they represent distinct contributions
   - May be too granular for CV

### Low Priority:

6. **Early Workshop Papers**
   - Papers from 2007-2011 that were superseded by conference publications
   - Likely already represented in CV under conference versions

---

## Implementation Notes

### For pub-sync System:

1. **Category Metadata**
   - Add category/subcategory fields to JSONL format
   - Support hierarchical organization

2. **Automatic Categorization**
   - Use venue information to suggest categories
   - IPC entries: check for "ipc" in BibTeX key
   - Workshop papers: check for "ws" in key or venue
   - System demos: check for "demo" in key

3. **Category Validation**
   - Ensure each paper has exactly one primary category
   - Allow optional secondary categories/tags

4. **Website Display**
   - Group by category on website
   - Allow filtering by category
   - Show subcategory within each group

---

## Next Steps

1. Review proposed additions with user
2. Decide on final category structure
3. Update CV with new categories
4. Update pub-sync tools to support categories
5. Regenerate website with categorized publications