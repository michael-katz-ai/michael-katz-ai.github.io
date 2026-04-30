#!/usr/bin/env python3
"""
Cross-reference all publication sources to find papers that appear in some but not all.
Generate a markdown report for manual review.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def normalize_title(title):
    """Normalize title for comparison - remove punctuation, extra spaces, make lowercase."""
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)  # Remove LaTeX commands
    title = re.sub(r'[^\w\s]', '', title.lower())  # Remove punctuation
    title = re.sub(r'\s+', ' ', title).strip()  # Normalize spaces
    return title

def extract_cv_papers():
    """Extract papers from CV JSON."""
    json_path = Path("data/publications.json")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    papers = []
    for topic in data['topics']:
        for subtopic in topic['subtopics']:
            for paper in subtopic['papers']:
                papers.append({
                    'title': paper['title'],
                    'title_norm': normalize_title(paper['title']),
                    'year': paper.get('year', 0),
                    'authors': paper.get('authors', []),
                    'venue': paper.get('venue', ''),
                    'source': 'CV',
                    'topic': topic['title'],
                    'subtopic': subtopic['title']
                })
    return papers

def extract_html_papers():
    """Extract papers from old HTML."""
    html_path = Path("../publications.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    papers = []
    # Find all <li> items with papers
    year_sections = re.findall(r'<font size="\+1"><b>(\d{4})</b></font>(.*?)(?=<font size="\+1"><b>|$)', content, re.DOTALL)
    
    for year, section_content in year_sections:
        year = int(year)
        li_items = re.findall(r'<li>(.*?)</li>', section_content, re.DOTALL)
        
        for li_content in li_items:
            # Extract title
            title_match = re.search(r'<b>(.*?)</b>', li_content, re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                title = re.sub(r'<[^>]+>', '', title)
                title = re.sub(r'\s+', ' ', title).strip()
                
                if len(title) > 10:  # Reasonable title length
                    papers.append({
                        'title': title,
                        'title_norm': normalize_title(title),
                        'year': year,
                        'source': 'HTML'
                    })
    
    return papers

def extract_bibtex_papers():
    """Extract papers from BibTeX (with proper year extraction)."""
    bib_file = Path("/Users/michaelkatz/software/LaTeX/papers-shared/bib-ctpelok/literatur.bib")
    
    with open(bib_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    papers = []
    # Split into entries
    entries = []
    current_entry = []
    in_entry = False
    brace_count = 0
    
    for line in content.split('\n'):
        if line.strip().startswith('@'):
            if current_entry:
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
                entry_text = '\n'.join(current_entry)
                if 'Michael Katz' in entry_text or 'M. Katz' in entry_text:
                    entries.append(entry_text)
                current_entry = []
                in_entry = False
    
    if current_entry:
        entry_text = '\n'.join(current_entry)
        if 'Michael Katz' in entry_text or 'M. Katz' in entry_text:
            entries.append(entry_text)
    
    # Parse entries
    for entry_text in entries:
        # Extract title
        title_match = re.search(r'title\s*=\s*["{]([^"}]+)["}]', entry_text, re.IGNORECASE | re.DOTALL)
        if not title_match:
            continue
        
        title = title_match.group(1).strip()
        title = re.sub(r'\{\\[a-zA-Z]+\s+([^}]+)\}', r'\1', title)
        title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
        title = re.sub(r'[{}]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Extract year (direct or from crossref key)
        year = 0
        year_match = re.search(r'year\s*=\s*["{]?(\d{4})["}]?', entry_text)
        if year_match:
            year = int(year_match.group(1))
        else:
            # Try to extract from crossref key (e.g., icaps2023)
            crossref_match = re.search(r'crossref\s*=\s*["{]([^"}]+)["}]', entry_text)
            if crossref_match:
                crossref_key = crossref_match.group(1)
                year_in_key = re.search(r'(\d{4})', crossref_key)
                if year_in_key:
                    year = int(year_in_key.group(1))
        
        # Extract BibTeX key
        key_match = re.match(r'@\w+\{([^,]+),', entry_text)
        bibtex_key = key_match.group(1) if key_match else ''
        
        papers.append({
            'title': title,
            'title_norm': normalize_title(title),
            'year': year,
            'source': 'BibTeX',
            'bibtex_key': bibtex_key
        })
    
    return papers

print("Extracting papers from all sources...")
cv_papers = extract_cv_papers()
html_papers = extract_html_papers()
bibtex_papers = extract_bibtex_papers()

print(f"CV: {len(cv_papers)} papers")
print(f"HTML: {len(html_papers)} papers")
print(f"BibTeX: {len(bibtex_papers)} papers")

# Create index by normalized title
all_papers = {}

for paper in cv_papers:
    norm_title = paper['title_norm']
    if norm_title not in all_papers:
        all_papers[norm_title] = {'sources': set(), 'data': {}}
    all_papers[norm_title]['sources'].add('CV')
    all_papers[norm_title]['data']['CV'] = paper

for paper in html_papers:
    norm_title = paper['title_norm']
    if norm_title not in all_papers:
        all_papers[norm_title] = {'sources': set(), 'data': {}}
    all_papers[norm_title]['sources'].add('HTML')
    all_papers[norm_title]['data']['HTML'] = paper

for paper in bibtex_papers:
    norm_title = paper['title_norm']
    if norm_title not in all_papers:
        all_papers[norm_title] = {'sources': set(), 'data': {}}
    all_papers[norm_title]['sources'].add('BibTeX')
    all_papers[norm_title]['data']['BibTeX'] = paper

# Categorize papers
in_all_three = []
in_cv_html = []
in_cv_bibtex = []
in_html_bibtex = []
only_cv = []
only_html = []
only_bibtex = []

for norm_title, info in all_papers.items():
    sources = info['sources']
    data = info['data']
    
    if len(sources) == 3:
        in_all_three.append(data)
    elif sources == {'CV', 'HTML'}:
        in_cv_html.append(data)
    elif sources == {'CV', 'BibTeX'}:
        in_cv_bibtex.append(data)
    elif sources == {'HTML', 'BibTeX'}:
        in_html_bibtex.append(data)
    elif sources == {'CV'}:
        only_cv.append(data)
    elif sources == {'HTML'}:
        only_html.append(data)
    elif sources == {'BibTeX'}:
        only_bibtex.append(data)

# Generate markdown report
report = []
report.append("# Publication Cross-Reference Analysis")
report.append("")
report.append(f"**Analysis Date:** 2025-01-15")
report.append("")
report.append("## Summary")
report.append("")
report.append(f"- **Total unique papers:** {len(all_papers)}")
report.append(f"- **In all three sources:** {len(in_all_three)}")
report.append(f"- **In CV + HTML only:** {len(in_cv_html)}")
report.append(f"- **In CV + BibTeX only:** {len(in_cv_bibtex)}")
report.append(f"- **In HTML + BibTeX only:** {len(in_html_bibtex)}")
report.append(f"- **Only in CV:** {len(only_cv)}")
report.append(f"- **Only in HTML:** {len(only_html)}")
report.append(f"- **Only in BibTeX:** {len(only_bibtex)}")
report.append("")

def format_paper_entry(data, sources):
    """Format a paper entry for the report."""
    lines = []
    # Get the most complete data
    paper = data.get('CV') or data.get('BibTeX') or data.get('HTML')
    
    lines.append(f"### {paper['title']}")
    lines.append(f"**Year:** {paper.get('year', 'Unknown')}")
    
    if 'CV' in data:
        cv_paper = data['CV']
        lines.append(f"**CV Topic:** {cv_paper.get('topic', 'N/A')} → {cv_paper.get('subtopic', 'N/A')}")
        if cv_paper.get('venue'):
            lines.append(f"**Venue:** {cv_paper['venue']}")
    
    if 'BibTeX' in data:
        bib_paper = data['BibTeX']
        lines.append(f"**BibTeX Key:** `{bib_paper.get('bibtex_key', 'N/A')}`")
    
    lines.append(f"**Sources:** {', '.join(sorted(sources))}")
    lines.append("")
    return lines

# Papers only in CV (not in HTML or BibTeX)
if only_cv:
    report.append("## Papers Only in CV")
    report.append("")
    report.append(f"**Count:** {len(only_cv)}")
    report.append("")
    report.append("These papers appear in the CV but are missing from both the old HTML and BibTeX database.")
    report.append("**Action:** Consider adding to BibTeX for completeness.")
    report.append("")
    for data in sorted(only_cv, key=lambda x: x['CV'].get('year', 0), reverse=True):
        report.extend(format_paper_entry(data, {'CV'}))

# Papers only in HTML
if only_html:
    report.append("## Papers Only in HTML")
    report.append("")
    report.append(f"**Count:** {len(only_html)}")
    report.append("")
    report.append("These papers appear in the old HTML but are missing from both CV and BibTeX.")
    report.append("**Action:** Review if these should be added to CV or if they were intentionally removed.")
    report.append("")
    for data in sorted(only_html, key=lambda x: x['HTML'].get('year', 0), reverse=True):
        report.extend(format_paper_entry(data, {'HTML'}))

# Papers only in BibTeX
if only_bibtex:
    report.append("## Papers Only in BibTeX")
    report.append("")
    report.append(f"**Count:** {len(only_bibtex)}")
    report.append("")
    report.append("These papers appear in BibTeX but are missing from both CV and HTML.")
    report.append("**Action:** Review if these should be added to CV (workshops, demos, technical reports?).")
    report.append("")
    for data in sorted(only_bibtex, key=lambda x: x['BibTeX'].get('year', 0), reverse=True):
        report.extend(format_paper_entry(data, {'BibTeX'}))

# Papers in CV + HTML but not BibTeX
if in_cv_html:
    report.append("## Papers in CV + HTML (Missing from BibTeX)")
    report.append("")
    report.append(f"**Count:** {len(in_cv_html)}")
    report.append("")
    report.append("**Action:** Add these to BibTeX database.")
    report.append("")
    for data in sorted(in_cv_html, key=lambda x: x['CV'].get('year', 0), reverse=True):
        report.extend(format_paper_entry(data, {'CV', 'HTML'}))

# Papers in CV + BibTeX but not HTML
if in_cv_bibtex:
    report.append("## Papers in CV + BibTeX (Missing from HTML)")
    report.append("")
    report.append(f"**Count:** {len(in_cv_bibtex)}")
    report.append("")
    report.append("These are likely newer papers (2024-2026) that weren't in the old HTML.")
    report.append("")
    for data in sorted(in_cv_bibtex, key=lambda x: x['CV'].get('year', 0), reverse=True):
        report.extend(format_paper_entry(data, {'CV', 'BibTeX'}))

# Papers in HTML + BibTeX but not CV
if in_html_bibtex:
    report.append("## Papers in HTML + BibTeX (Missing from CV)")
    report.append("")
    report.append(f"**Count:** {len(in_html_bibtex)}")
    report.append("")
    report.append("**Action:** Review if these should be added to CV.")
    report.append("")
    for data in sorted(in_html_bibtex, key=lambda x: x['HTML'].get('year', 0), reverse=True):
        report.extend(format_paper_entry(data, {'HTML', 'BibTeX'}))

# Write report
report_path = Path("PUBLICATIONS_CROSS_REFERENCE.md")
with open(report_path, 'w') as f:
    f.write('\n'.join(report))

print(f"\nReport saved to: {report_path}")
print("\nSummary:")
print(f"  In all three sources: {len(in_all_three)}")
print(f"  Only in CV: {len(only_cv)}")
print(f"  Only in HTML: {len(only_html)}")
print(f"  Only in BibTeX: {len(only_bibtex)}")
print(f"  In CV+HTML (not BibTeX): {len(in_cv_html)}")
print(f"  In CV+BibTeX (not HTML): {len(in_cv_bibtex)}")
print(f"  In HTML+BibTeX (not CV): {len(in_html_bibtex)}")

# Made with Bob
