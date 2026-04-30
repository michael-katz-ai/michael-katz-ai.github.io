#!/usr/bin/env python3
"""
Extract publications from old HTML and create two JSON files:
1. publications.json - Curated list organized by research topics (from CV)
2. publications-full.json - Complete chronological list of all publications
"""

import json
import re
from pathlib import Path

# Read the old publications HTML
html_path = Path("../publications.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

def extract_paper_info(li_content):
    """Extract paper information from an <li> element content."""
    # Extract title (usually in <b> tags)
    title_match = re.search(r'<b>(.*?)</b>', li_content, re.DOTALL)
    if not title_match:
        return None
    
    title = title_match.group(1).strip()
    title = re.sub(r'<[^>]+>', '', title)  # Remove any HTML tags
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Extract authors (before the title usually)
    authors_text = li_content[:title_match.start()].strip()
    authors_text = re.sub(r'<[^>]+>', '', authors_text)
    authors_text = re.sub(r'\s+', ' ', authors_text).strip()
    
    # Split authors by comma, "and", or other separators
    if authors_text:
        # Handle various author formats
        authors_text = authors_text.rstrip(',').rstrip('.')
        authors = [a.strip() for a in re.split(r',\s*(?:and\s+)?|\s+and\s+', authors_text) if a.strip()]
        # Clean up author names
        authors = [re.sub(r'\s+', ' ', a).strip() for a in authors if len(a.strip()) > 1]
    else:
        authors = []
    
    # Extract venue and year
    venue_match = re.search(r'<i>(.*?)</i>', li_content)
    venue = venue_match.group(1).strip() if venue_match else ""
    venue = re.sub(r'\s+', ' ', venue).strip()
    
    year_match = re.search(r'\b(19|20)\d{2}\b', li_content)
    year = int(year_match.group(0)) if year_match else 0
    
    # Extract PDF link
    pdf_match = re.search(r'href=["\']([^"\']*\.pdf)["\']', li_content)
    pdf_link = pdf_match.group(1) if pdf_match else ""
    
    # Extract slides link
    slides_match = re.search(r'href=["\']([^"\']*slides[^"\']*\.pdf)["\']', li_content, re.IGNORECASE)
    slides_link = slides_match.group(1) if slides_match else ""
    
    # Determine type based on venue
    paper_type = "conference"
    if "Journal" in venue or "AIJ" in venue or "JAIR" in venue or "journal" in venue.lower():
        paper_type = "journal"
    elif "Workshop" in venue or "workshop" in venue.lower():
        paper_type = "workshop"
    elif "Technical report" in li_content or "Tech report" in li_content:
        paper_type = "technical-report"
    elif "Proceedings" in venue and "eds" in li_content:
        paper_type = "proceedings"
    elif "Demo" in venue or "Demonstration" in venue:
        paper_type = "demo"
    
    # Check for awards
    award = None
    if "ICAPS Influential Paper" in li_content or "test-of-time" in li_content:
        award = "ICAPS Influential Paper Award 2023"
    elif "Winner" in li_content and "ICAPS Best Dissertation Award" in li_content:
        award = "ICAPS Best Dissertation Award 2011"
    elif "Best" in li_content and "Award" in li_content:
        award_match = re.search(r'(Best[^<.]*Award[^<.]*)', li_content)
        if award_match:
            award = award_match.group(1).strip()
    
    links = {}
    if pdf_link:
        links["pdf"] = pdf_link
    if slides_link:
        links["slides"] = slides_link
    
    return {
        "title": title,
        "authors": authors,
        "venue": venue,
        "year": year,
        "type": paper_type,
        "links": links,
        "award": award
    }

# Extract all papers from HTML
papers_by_year = {}
year_sections = re.findall(r'<font size="\+1"><b>(\d{4})</b></font>(.*?)(?=<font size="\+1"><b>|$)', html_content, re.DOTALL)

for year, section_content in year_sections:
    year = int(year)
    # Find all <li> elements in this section
    li_items = re.findall(r'<li>(.*?)</li>', section_content, re.DOTALL)
    
    for li_content in li_items:
        paper_info = extract_paper_info(li_content)
        if paper_info and paper_info['title']:
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(paper_info)

# Create full chronological list
full_publications = {
    "metadata": {
        "lastUpdated": "2025-01-15",
        "totalPapers": 0,
        "description": "Complete chronological list of all publications"
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

total_papers = 0
for year in sorted(papers_by_year.keys(), reverse=True):
    papers = papers_by_year[year]
    for i, paper in enumerate(papers):
        paper['id'] = f"paper-{year}-{i+1}"
        total_papers += 1
    
    full_publications["years"].append({
        "year": year,
        "papers": papers
    })

full_publications["metadata"]["totalPapers"] = total_papers

# Write full list
output_full = Path("data/publications-full.json")
output_full.parent.mkdir(exist_ok=True)
with open(output_full, 'w', encoding='utf-8') as f:
    json.dump(full_publications, f, indent=2, ensure_ascii=False)

print(f"Created publications-full.json with {total_papers} papers")

# Now create the curated list based on CV
# Read the CV LaTeX to get exact paper titles
cv_path = Path("/Users/michaelkatz/software/LaTeX/papers-old/cv/chatgpt-cv.tex")
with open(cv_path, 'r', encoding='utf-8') as f:
    cv_content = f.read()

# Extract paper titles from CV by finding \item entries
cv_papers = []
# Find all \item entries that contain paper information
item_pattern = r'\\item\s+(.*?)(?=\\item|\\end\{itemize\}|\\subsection)'
items = re.findall(item_pattern, cv_content, re.DOTALL)

for item in items:
    # Look for title in {\it ...} or {\bf ...}
    title_match = re.search(r'\{\\it\s+(.*?)\}', item)
    if not title_match:
        title_match = re.search(r'\{\\bf\s+(.*?)\}', item)
    
    if title_match:
        title = title_match.group(1).strip()
        # Clean up LaTeX commands
        title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
        title = re.sub(r'\\[a-zA-Z]+', '', title)
        title = title.strip()
        if len(title) > 10:  # Reasonable title length
            cv_papers.append(title)

print(f"\nFound {len(cv_papers)} papers in CV")

# Now let's manually create the curated structure based on CV organization
# This will be more accurate than automated matching
curated_publications = {
    "metadata": {
        "lastUpdated": "2025-01-15",
        "totalPapers": 0,
        "description": "Curated publications organized by research topics"
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
    "topics": []
}

# For now, let's use the existing categorized papers and note that manual curation is needed
# The user can manually add the missing papers or we can create a more sophisticated matcher

print("\nNote: The curated publications.json needs manual completion.")
print("The extraction script has created publications-full.json with all papers.")
print("You can now manually organize papers from publications-full.json into publications.json")
print("following the CV structure.")

# Write a template curated structure
output_curated = Path("data/publications.json")
with open(output_curated, 'w', encoding='utf-8') as f:
    json.dump(curated_publications, f, indent=2, ensure_ascii=False)

print(f"\nCreated template publications.json")
print(f"\nSummary:")
print(f"- publications-full.json: {total_papers} papers (complete chronological list)")
print(f"- publications.json: Template created (needs manual curation)")
