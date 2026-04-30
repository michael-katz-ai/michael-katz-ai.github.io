#!/usr/bin/env python3
"""
Cross-reference all publication sources using proper BibTeX parsing.
Ignore Zenodo entries.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import bibtexparser
from bibtexparser.bparser import BibTexParser

def clean_latex(text):
    """Remove LaTeX commands and clean up text."""
    # Handle math expressions first (before removing braces)
    text = text.replace(r'$^{\ast}$', '*')
    text = text.replace(r'$^\ast$', '*')
    text = text.replace(r'$^{*}$', '*')
    text = text.replace(r'$*$', '*')
    
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\{\\it\s+([^}]*)\}', r'\1', text)
    text = re.sub(r'\{\\bf\s+([^}]*)\}', r'\1', text)
    text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\\&', '&', text)
    text = re.sub(r'\\\$', '$', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_title(title):
    """Normalize title for comparison."""
    # Handle common LaTeX math expressions
    title = title.replace(r'$^{\ast}$', '*')
    title = title.replace(r'$^\ast$', '*')
    title = title.replace(r'$^{*}$', '*')
    title = title.replace(r'$*$', '*')
    
    # Remove LaTeX commands
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
    title = re.sub(r'\{([^}]*)\}', r'\1', title)
    
    # Remove remaining $ signs
    title = title.replace('$', '')
    
    # Remove punctuation and make lowercase
    title = re.sub(r'[^\w\s]', '', title.lower())
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def extract_title_from_item(item_text):
    """Extract title from {\it ...} handling nested braces."""
    # Find {\it and then match braces properly
    start = item_text.find('{\\it')
    if start == -1:
        return None
    
    # Start after {\it
    pos = start + 4  # len('{\\it')
    brace_count = 1
    title_start = pos
    
    while pos < len(item_text) and brace_count > 0:
        if item_text[pos] == '{':
            brace_count += 1
        elif item_text[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count == 0:
        title = item_text[title_start:pos-1].strip()
        return clean_latex(title)
    return None

def extract_cv_papers():
    """Extract papers directly from CV LaTeX file using proper parsing."""
    cv_path = Path("/Users/michaelkatz/software/LaTeX/papers-old/cv/chatgpt-cv.tex")
    
    with open(cv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    papers = []
    
    # Find all \item entries that contain paper information
    # Pattern: \item followed by text containing {\it Title}
    items = re.findall(r'\\item\s+([^\n]+(?:\n(?!\s*\\item)[^\n]+)*)', content, re.MULTILINE)
    
    for item_text in items:
        # Extract title (in {\it ...}) with proper brace matching
        title = extract_title_from_item(item_text)
        if not title:
            continue
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', item_text)
        year = int(year_match.group(0)) if year_match else 0
        
        # Extract authors (before the title)
        title_start = item_text.find('{\\it')
        authors = []
        if title_start > 0:
            author_text = item_text[:title_start]
            author_text = clean_latex(author_text)
            authors = [a.strip() for a in re.split(r',\s*|\s+and\s+', author_text) if a.strip() and len(a.strip()) > 2]
            authors = [a for a in authors if not any(x in a.lower() for x in ['proceedings', 'conference', 'journal'])]
            authors = [a.rstrip('.,') for a in authors]
        
        papers.append({
            'title': title,
            'title_norm': normalize_title(title),
            'year': year,
            'authors': authors,
            'venue': '',
            'source': 'CV',
            'topic': '',
            'subtopic': ''
        })
    
    return papers

def extract_html_papers():
    """Extract papers from old HTML."""
    html_path = Path("../publications.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    papers = []
    year_sections = re.findall(r'<font size="\+1"><b>(\d{4})</b></font>(.*?)(?=<font size="\+1"><b>|$)', content, re.DOTALL)
    
    for year, section_content in year_sections:
        year = int(year)
        li_items = re.findall(r'<li>(.*?)</li>', section_content, re.DOTALL)
        
        for li_content in li_items:
            title_match = re.search(r'<b>(.*?)</b>', li_content, re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                title = re.sub(r'<[^>]+>', '', title)
                title = re.sub(r'\s+', ' ', title).strip()
                
                if len(title) > 10:
                    papers.append({
                        'title': title,
                        'title_norm': normalize_title(title),
                        'year': year,
                        'source': 'HTML'
                    })
    
    return papers

def extract_bibtex_papers():
    """Extract papers from BibTeX using proper parser."""
    bib_dir = Path("/Users/michaelkatz/software/LaTeX/papers-shared/bib-ctpelok")
    
    # Load abbreviations first, then main file
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    
    # Read abbreviations
    abbrv_file = bib_dir / "abbrv.bib"
    if abbrv_file.exists():
        with open(abbrv_file, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f, parser=parser)
    else:
        bib_database = bibtexparser.bibdatabase.BibDatabase()
    
    # Read main file
    bib_file = bib_dir / "literatur.bib"
    with open(bib_file, 'r', encoding='utf-8') as f:
        main_db = bibtexparser.load(f, parser=parser)
        # Merge databases
        bib_database.entries.extend(main_db.entries)
    
    papers = []
    for entry in bib_database.entries:
        # Skip Zenodo entries
        if 'zenodo' in entry.get('ID', '').lower():
            continue
        
        # Check if Michael Katz is an author
        author_field = entry.get('author', '')
        if 'Michael Katz' not in author_field and 'M. Katz' not in author_field:
            continue
        
        title = entry.get('title', '').strip()
        if not title or len(title) < 10:
            continue
        
        # Clean title
        title = re.sub(r'\{([^}]*)\}', r'\1', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Get year
        year = 0
        if 'year' in entry:
            try:
                year = int(entry['year'])
            except:
                pass
        
        # If no year, try to extract from crossref key
        if year == 0 and 'crossref' in entry:
            crossref_key = entry['crossref']
            year_match = re.search(r'(\d{4})', crossref_key)
            if year_match:
                year = int(year_match.group(1))
        
        # Get venue
        venue = entry.get('booktitle', entry.get('journal', ''))
        venue = re.sub(r'\{([^}]*)\}', r'\1', venue)
        venue = re.sub(r'\s+', ' ', venue).strip()
        
        papers.append({
            'title': title,
            'title_norm': normalize_title(title),
            'year': year,
            'venue': venue,
            'source': 'BibTeX',
            'bibtex_key': entry.get('ID', ''),
            'bibtex_type': entry.get('ENTRYTYPE', '')
        })
    
    return papers

print("Extracting papers from all sources...")
print("(Using proper BibTeX parser, ignoring Zenodo entries)")

cv_papers = extract_cv_papers()
html_papers = extract_html_papers()
bibtex_papers = extract_bibtex_papers()

print(f"\nCV: {len(cv_papers)} papers")
print(f"HTML: {len(html_papers)} papers")
print(f"BibTeX: {len(bibtex_papers)} papers (excluding Zenodo)")

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
report.append(f"**Note:** Zenodo entries excluded from BibTeX analysis")
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
        if bib_paper.get('venue') and 'CV' not in data:
            lines.append(f"**Venue:** {bib_paper['venue']}")
    
    lines.append(f"**Sources:** {', '.join(sorted(sources))}")
    lines.append("")
    return lines

# Papers only in CV
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
