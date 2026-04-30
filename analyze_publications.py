#!/usr/bin/env python3
"""
Analyze and reconcile publications from multiple sources:
1. CV LaTeX file
2. BibTeX database
3. Old HTML

Create a comprehensive report of all publications.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def parse_bibtex_entry(entry_text):
    """Parse a single BibTeX entry."""
    # Extract entry type and key
    match = re.match(r'@(\w+)\{([^,]+),', entry_text)
    if not match:
        return None
    
    entry_type = match.group(1).lower()
    key = match.group(2).strip()
    
    # Extract fields
    fields = {}
    field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}|\{([^}]*)\}'
    
    for match in re.finditer(field_pattern, entry_text):
        field_name = match.group(1)
        if field_name:
            field_value = match.group(2) if match.group(2) else match.group(3)
            if field_value:
                fields[field_name.lower()] = field_value.strip()
    
    # Extract title more carefully
    title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry_text, re.IGNORECASE)
    if title_match:
        fields['title'] = title_match.group(1).strip()
    
    # Extract year
    year_match = re.search(r'year\s*=\s*\{?(\d{4})\}?', entry_text)
    if year_match:
        fields['year'] = int(year_match.group(1))
    
    return {
        'type': entry_type,
        'key': key,
        'fields': fields
    }

def extract_bibtex_entries(bib_file):
    """Extract all BibTeX entries with Michael Katz as author."""
    with open(bib_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all entries
    entries = []
    entry_pattern = r'@\w+\{[^@]+'
    
    for match in re.finditer(entry_pattern, content):
        entry_text = match.group(0)
        
        # Check if Michael Katz is an author
        if re.search(r'author.*?Katz.*?Michael|author.*?Michael.*?Katz|author.*?M\.\s*Katz', entry_text, re.IGNORECASE | re.DOTALL):
            parsed = parse_bibtex_entry(entry_text)
            if parsed and 'title' in parsed['fields']:
                entries.append(parsed)
    
    return entries

def normalize_title(title):
    """Normalize title for comparison."""
    # Remove LaTeX commands, punctuation, extra spaces
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
    title = re.sub(r'[^\w\s]', '', title.lower())
    title = re.sub(r'\s+', ' ', title).strip()
    return title

# Load existing JSON data
json_path = Path("data/publications.json")
with open(json_path, 'r') as f:
    json_data = json.load(f)

# Extract titles from JSON
json_titles = set()
json_papers = []
for topic in json_data['topics']:
    for subtopic in topic['subtopics']:
        for paper in subtopic['papers']:
            norm_title = normalize_title(paper['title'])
            json_titles.add(norm_title)
            json_papers.append({
                'title': paper['title'],
                'year': paper['year'],
                'venue': paper.get('venue', ''),
                'source': 'JSON/CV'
            })

print(f"Papers in JSON (from CV): {len(json_papers)}")

# Extract from BibTeX
bib_file = Path("/Users/michaelkatz/software/LaTeX/papers-shared/bib-ctpelok/literatur.bib")
bib_entries = extract_bibtex_entries(bib_file)

bib_titles = set()
bib_papers = []
for entry in bib_entries:
    title = entry['fields'].get('title', '')
    if title:
        norm_title = normalize_title(title)
        bib_titles.add(norm_title)
        bib_papers.append({
            'title': title,
            'year': entry['fields'].get('year', 0),
            'venue': entry['fields'].get('booktitle', entry['fields'].get('journal', '')),
            'type': entry['type'],
            'key': entry['key'],
            'source': 'BibTeX'
        })

print(f"Papers in BibTeX: {len(bib_papers)}")

# Find papers in BibTeX but not in JSON
missing_in_json = []
for bib_paper in bib_papers:
    norm_title = normalize_title(bib_paper['title'])
    if norm_title not in json_titles:
        missing_in_json.append(bib_paper)

# Find papers in JSON but not in BibTeX
missing_in_bib = []
for json_paper in json_papers:
    norm_title = normalize_title(json_paper['title'])
    if norm_title not in bib_titles:
        missing_in_bib.append(json_paper)

# Print report
print(f"\n{'='*80}")
print("PUBLICATION RECONCILIATION REPORT")
print(f"{'='*80}\n")

print(f"Total papers in JSON (from CV): {len(json_papers)}")
print(f"Total papers in BibTeX: {len(bib_papers)}")
print(f"Papers in both sources: {len(json_titles & bib_titles)}")

print(f"\n{'='*80}")
print(f"Papers in BibTeX but NOT in JSON/CV: {len(missing_in_json)}")
print(f"{'='*80}")
if missing_in_json:
    for i, paper in enumerate(sorted(missing_in_json, key=lambda x: x.get('year', 0), reverse=True), 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Year: {paper.get('year', 'N/A')}, Type: {paper.get('type', 'N/A')}")
        print(f"   Venue: {paper.get('venue', 'N/A')}")
        print(f"   BibTeX key: {paper.get('key', 'N/A')}")

print(f"\n{'='*80}")
print(f"Papers in JSON/CV but NOT in BibTeX: {len(missing_in_bib)}")
print(f"{'='*80}")
if missing_in_bib:
    for i, paper in enumerate(sorted(missing_in_bib, key=lambda x: x.get('year', 0), reverse=True), 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Year: {paper.get('year', 'N/A')}")
        print(f"   Venue: {paper.get('venue', 'N/A')}")

# Save detailed report to file
report_path = Path("data/publications_reconciliation.json")
report = {
    "summary": {
        "json_count": len(json_papers),
        "bibtex_count": len(bib_papers),
        "in_both": len(json_titles & bib_titles),
        "missing_in_json": len(missing_in_json),
        "missing_in_bibtex": len(missing_in_bib)
    },
    "missing_in_json": missing_in_json,
    "missing_in_bibtex": missing_in_bib
}

with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n{'='*80}")
print(f"Detailed report saved to: {report_path}")
print(f"{'='*80}")
