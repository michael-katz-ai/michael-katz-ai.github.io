#!/usr/bin/env python3
"""
Extract ALL publications from BibTeX database (the authoritative source).
This will be the complete list to use for both chronological and topic-based views.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def parse_bibtex_file(bib_file):
    """Parse BibTeX file and extract all entries with Michael Katz as author."""
    with open(bib_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Split into individual entries
    entries = []
    current_entry = []
    in_entry = False
    brace_count = 0
    
    for line in content.split('\n'):
        if line.strip().startswith('@'):
            if current_entry:
                # Process previous entry
                entry_text = '\n'.join(current_entry)
                if 'Michael Katz' in entry_text or 'M. Katz' in entry_text:
                    entries.append(entry_text)
            current_entry = [line]
            in_entry = True
            brace_count = line.count('{') - line.count('}')
        elif in_entry:
            current_entry.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                # Entry complete
                entry_text = '\n'.join(current_entry)
                if 'Michael Katz' in entry_text or 'M. Katz' in entry_text:
                    entries.append(entry_text)
                current_entry = []
                in_entry = False
    
    # Process last entry if any
    if current_entry:
        entry_text = '\n'.join(current_entry)
        if 'Michael Katz' in entry_text or 'M. Katz' in entry_text:
            entries.append(entry_text)
    
    return entries

def parse_entry(entry_text):
    """Parse a single BibTeX entry into structured data."""
    # Extract entry type and key
    match = re.match(r'@(\w+)\{([^,]+),', entry_text)
    if not match:
        return None
    
    entry_type = match.group(1).lower()
    key = match.group(2).strip()
    
    # Extract fields
    paper = {
        'bibtex_key': key,
        'bibtex_type': entry_type,
        'title': '',
        'authors': [],
        'venue': '',
        'year': 0,
        'type': 'conference'
    }
    
    # Extract title
    title_match = re.search(r'title\s*=\s*["{]([^"}]+)["}]', entry_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        # Clean up LaTeX commands
        title = re.sub(r'\{\\[a-zA-Z]+\s+([^}]+)\}', r'\1', title)
        title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
        title = re.sub(r'[{}]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        paper['title'] = title
    
    # Extract authors
    author_match = re.search(r'author\s*=\s*["{]([^"}]+)["}]', entry_text, re.IGNORECASE | re.DOTALL)
    if author_match:
        authors_text = author_match.group(1)
        # Split by 'and'
        authors = [a.strip() for a in re.split(r'\s+and\s+', authors_text)]
        # Clean up LaTeX
        authors = [re.sub(r'\{\\[a-zA-Z]+\s+([^}]+)\}', r'\1', a) for a in authors]
        authors = [re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', a) for a in authors]
        authors = [re.sub(r'[{}]', '', a).strip() for a in authors]
        paper['authors'] = authors
    
    # Extract year
    year_match = re.search(r'year\s*=\s*["{]?(\d{4})["}]?', entry_text)
    if year_match:
        paper['year'] = int(year_match.group(1))
    
    # Extract venue (booktitle or journal)
    venue_match = re.search(r'(?:booktitle|journal)\s*=\s*["{]([^"}]+)["}]', entry_text, re.IGNORECASE | re.DOTALL)
    if venue_match:
        venue = venue_match.group(1).strip()
        venue = re.sub(r'\{\\[a-zA-Z]+\s+([^}]+)\}', r'\1', venue)
        venue = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', venue)
        venue = re.sub(r'[{}]', '', venue)
        venue = re.sub(r'\s+', ' ', venue).strip()
        paper['venue'] = venue
    
    # Determine paper type
    if entry_type in ['article', 'journal']:
        paper['type'] = 'journal'
    elif 'workshop' in entry_text.lower() or 'ws' in key.lower():
        paper['type'] = 'workshop'
    else:
        paper['type'] = 'conference'
    
    # Extract pages if available
    pages_match = re.search(r'pages\s*=\s*["{]([^"}]+)["}]', entry_text)
    if pages_match:
        paper['pages'] = pages_match.group(1).strip()
    
    return paper

# Parse BibTeX file
bib_file = Path("/Users/michaelkatz/software/LaTeX/papers-shared/bib-ctpelok/literatur.bib")
print(f"Parsing {bib_file}...")
entries = parse_bibtex_file(bib_file)
print(f"Found {len(entries)} entries with Michael Katz as author")

# Parse each entry
papers = []
for entry_text in entries:
    paper = parse_entry(entry_text)
    if paper and paper['title']:
        papers.append(paper)

print(f"Successfully parsed {len(papers)} papers")

# Sort by year (descending)
papers.sort(key=lambda x: x['year'], reverse=True)

# Create chronological JSON
chronological_data = {
    "metadata": {
        "lastUpdated": "2025-01-15",
        "totalPapers": len(papers),
        "description": "Complete chronological list from BibTeX database",
        "source": "literatur.bib"
    },
    "thesis": {
        "title": "Implicit Abstraction Heuristics for Cost-Optimal Planning",
        "university": "Technion - Israel Institute of Technology",
        "year": 2010,
        "award": "ICAPS Best Dissertation Award 2011",
        "links": {
            "pdf": "PHD/MichaelKatzPhD.pdf",
            "slides": "PHD/PhDAwardICAPS-talk.pdf"
        }
    },
    "years": []
}

# Group by year
papers_by_year = defaultdict(list)
for paper in papers:
    papers_by_year[paper['year']].append(paper)

# Create year sections
for year in sorted(papers_by_year.keys(), reverse=True):
    year_papers = papers_by_year[year]
    for i, paper in enumerate(year_papers):
        paper['id'] = f"paper-{year}-{i+1}"
    
    chronological_data["years"].append({
        "year": year,
        "papers": year_papers
    })

# Save chronological JSON
output_path = Path("data/publications-complete.json")
output_path.parent.mkdir(exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(chronological_data, f, indent=2, ensure_ascii=False)

print(f"\nSaved complete chronological list to: {output_path}")
print(f"Total papers: {len(papers)}")

# Print summary by year
print("\nPapers by year:")
for year in sorted(papers_by_year.keys(), reverse=True):
    print(f"  {year}: {len(papers_by_year[year])} papers")

print(f"\nThis is the COMPLETE list from BibTeX (authoritative source)")
print(f"Use this as the basis for both chronological and topic-based views")

# Made with Bob
