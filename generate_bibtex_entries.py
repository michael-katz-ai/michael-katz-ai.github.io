#!/usr/bin/env python3
"""
Generate BibTeX entries for papers that need to be added to literatur.bib
"""

import json
import re

# Papers to add (from PUBLICATIONS_ADD_TO_Bib.md)
papers_to_add = [
    "Planning in the LLM Era: Building for Reliability and Efficiency",
    "Model Space Reasoning as Search in Feedback Space for Planning Domain Generation",
    "Simplifying Planning Tasks with Fact-Level Relevance Analysis",
    "QueryGym: Step-by-Step Interaction with Relational Databases",
    "Make Planning Research Rigorous Again!",
    "Transition Function Prediction in AI Planning Using LLMs",
    "Less is More: Learning Graph Tasks with Just LLMs",
    "Beyond Message Passing: Modern GNN Architectures for Online Planner Selection",
    "Guiding Hierarchical Reinforcement Learning in Partially Observable Environments with AI Planning",
    "Learning Parameterized Policies for Planning Annotated RL",
    "Scenario Planning In The Wild: A Neuro-Symbolic Approach",
    "IBM Scenario Planning Advisor: A Neuro-Symbolic ERM solution",
    "Democratizing Usage of Planning Systems by Facilitating Research in Algorithm Selection for Planning",
    "The Role of IPC in Setting Standards for Experimental Evaluation in Planning Research",
]

def normalize_title(title):
    """Normalize title for comparison"""
    # Remove punctuation and extra spaces
    title = re.sub(r'[^\w\s]', '', title.lower())
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def generate_bibtex_key(authors, year, title):
    """Generate a BibTeX key in the format: firstauthor:venue:year"""
    # Get first author's last name
    first_author = authors[0].strip()
    # Extract last name (assume format: "First Last" or "First Middle Last")
    parts = first_author.split()
    last_name = parts[-1].lower()
    
    # Get first significant word from title (not "the", "a", "an")
    title_words = title.lower().split()
    significant_word = None
    for word in title_words:
        if word not in ['the', 'a', 'an', 'in', 'on', 'at', 'for', 'with', 'and', 'or']:
            significant_word = word[:4]  # First 4 chars
            break
    
    if not significant_word:
        significant_word = title_words[0][:4]
    
    return f"{last_name}:{significant_word}:{year}"

def format_authors_bibtex(authors):
    """Format authors for BibTeX"""
    return " and ".join(authors)

def get_venue_type(venue, paper_type):
    """Determine BibTeX entry type and format venue"""
    venue_lower = venue.lower()
    
    # Conference proceedings
    if any(conf in venue_lower for conf in ['aaai', 'ijcai', 'icaps', 'neurips', 'ecai', 'socs']):
        return 'inproceedings', venue
    
    # Journals
    if any(j in venue_lower for j in ['journal', 'jair', 'ai magazine']):
        return 'article', venue
    
    # Workshops
    if 'workshop' in venue_lower or paper_type == 'workshop':
        return 'inproceedings', venue
    
    # Technical reports, position papers, etc.
    if paper_type in ['position', 'demo', 'technical report']:
        return 'misc', venue
    
    # Default to inproceedings for conferences
    return 'inproceedings', venue

def generate_bibtex_entry(paper):
    """Generate a BibTeX entry for a paper"""
    title = paper['title']
    authors = paper['authors']
    venue = paper['venue']
    year = paper['year']
    paper_type = paper['type']
    
    # Generate key
    key = generate_bibtex_key(authors, year, title)
    
    # Determine entry type
    entry_type, formatted_venue = get_venue_type(venue, paper_type)
    
    # Format authors
    author_str = format_authors_bibtex(authors)
    
    # Build BibTeX entry
    entry = f"@{entry_type}{{{key},\n"
    entry += f"  author    = {{{author_str}}},\n"
    entry += f"  title     = {{{title}}},\n"
    
    if entry_type == 'inproceedings':
        entry += f"  booktitle = {{{formatted_venue}}},\n"
    elif entry_type == 'article':
        entry += f"  journal   = {{{formatted_venue}}},\n"
    else:  # misc
        entry += f"  howpublished = {{{formatted_venue}}},\n"
    
    entry += f"  year      = {{{year}}}\n"
    entry += "}\n"
    
    return entry

def main():
    # Load publications.json
    with open('data/publications.json', 'r') as f:
        data = json.load(f)
    
    # Normalize titles to add
    normalized_to_add = {normalize_title(t): t for t in papers_to_add}
    
    # Find papers in JSON
    found_papers = []
    
    for topic in data['topics']:
        for subtopic in topic['subtopics']:
            for paper in subtopic['papers']:
                normalized = normalize_title(paper['title'])
                if normalized in normalized_to_add:
                    found_papers.append(paper)
                    print(f"Found: {paper['title']}")
    
    print(f"\n\nFound {len(found_papers)} out of {len(papers_to_add)} papers\n")
    print("="*80)
    print("BibTeX Entries to Add to literatur.bib")
    print("="*80)
    print()
    
    # Generate BibTeX entries
    for paper in found_papers:
        entry = generate_bibtex_entry(paper)
        print(entry)
    
    # Check for missing papers
    found_titles = {normalize_title(p['title']) for p in found_papers}
    missing = [normalized_to_add[t] for t in normalized_to_add if t not in found_titles]
    
    if missing:
        print("\n" + "="*80)
        print("WARNING: Could not find these papers in publications.json:")
        print("="*80)
        for title in missing:
            print(f"  - {title}")

if __name__ == '__main__':
    main()
