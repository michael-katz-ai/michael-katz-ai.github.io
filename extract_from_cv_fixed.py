#!/usr/bin/env python3
"""
Extract ALL publications directly from CV LaTeX file - FIXED VERSION.
Handles all edge cases including special characters in subtopic titles.
"""

import json
import re
from pathlib import Path

# Read the CV LaTeX file
cv_path = Path("/Users/michaelkatz/software/LaTeX/papers-old/cv/chatgpt-cv.tex")
with open(cv_path, 'r', encoding='utf-8') as f:
    cv_content = f.read()

# Read the old HTML for PDF links
html_path = Path("../publications.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

def clean_latex(text):
    """Remove LaTeX commands and clean up text."""
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\{\\it\s+([^}]*)\}', r'\1', text)
    text = re.sub(r'\{\\bf\s+([^}]*)\}', r'\1', text)
    text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\\&', '&', text)  # Handle \& 
    text = re.sub(r'\\\$', '$', text)  # Handle \$
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def find_pdf_link(title, html_content):
    """Find PDF link for a paper in the HTML."""
    # Try to find by title
    title_clean = title[:40].replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    title_pattern = re.escape(title_clean)
    pattern = rf'{title_pattern}.*?href=["\']([^"\']*\.pdf)["\']'
    match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)
    return None

def extract_authors_venue_year(item_text):
    """Extract authors, venue, and year from LaTeX item."""
    authors = []
    venue = ""
    year = 0
    
    # Extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', item_text)
    if year_match:
        year = int(year_match.group(0))
    
    # Extract venue (in \textit{...})
    venue_match = re.search(r'\\textit\{([^}]+)\}', item_text)
    if venue_match:
        venue = clean_latex(venue_match.group(1))
    
    # Extract authors (before the title)
    # Find where the title starts (usually with {\it or {\bf)
    title_start = item_text.find('{\\it')
    if title_start == -1:
        title_start = item_text.find('{\\bf')
    
    if title_start > 0:
        author_text = item_text[:title_start]
        author_text = clean_latex(author_text)
        # Split by comma and "and"
        authors = [a.strip() for a in re.split(r',\s*|\s+and\s+', author_text) if a.strip() and len(a.strip()) > 2]
        # Filter out non-author text
        authors = [a for a in authors if not any(x in a.lower() for x in ['proceedings', 'conference', 'journal', 'volume', 'pages', 'number'])]
        # Remove trailing dots and commas
        authors = [a.rstrip('.,') for a in authors]
    
    return authors, venue, year

def determine_paper_type(venue):
    """Determine paper type from venue."""
    venue_lower = venue.lower()
    if 'journal' in venue_lower or 'aij' in venue_lower or 'jair' in venue_lower:
        return 'journal'
    elif 'workshop' in venue_lower:
        return 'workshop'
    else:
        return 'conference'

# Initialize publications structure
publications_data = {
    "metadata": {
        "lastUpdated": "2025-01-15",
        "totalPapers": 0,
        "description": "Publications organized by research topics (from CV)"
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

# Parse CV by sections
pub_section_match = re.search(r'\\section\*\{Publications By Topics\}(.*?)(?=\\end\{document\}|$)', cv_content, re.DOTALL)
if not pub_section_match:
    print("Could not find Publications By Topics section")
    exit(1)

pub_section = pub_section_match.group(1)

# Extract each subsection (topic)
subsection_pattern = r'\\subsection\*\{([^}]+)\}(.*?)(?=\\subsection\*|$)'
subsections = re.findall(subsection_pattern, pub_section, re.DOTALL)

topic_id_map = {
    "LLMs for Planning and Neuro-Symbolic Reasoning": "llms-planning",
    "Multiple Solutions for Classical Planning": "multiple-solutions",
    "Theory and Practice of Classical Planning": "theory-practice",
    "Planning and Reinforcement Learning": "planning-rl",
    "Applications, Data, and AI Planning Solutions": "applications",
    "Applications, Data, and AI Planning based solutions": "applications"
}

for topic_title, topic_content in subsections:
    topic_title_clean = clean_latex(topic_title)
    topic_id = topic_id_map.get(topic_title_clean, topic_title_clean.lower().replace(' ', '-'))
    
    # Extract description
    desc_match = re.search(r'\\vspace.*?\n(.*?)(?=\\item|\\begin\{itemize\})', topic_content, re.DOTALL)
    description = clean_latex(desc_match.group(1)) if desc_match else ""
    
    topic_entry = {
        "id": topic_id,
        "title": topic_title_clean,
        "description": description,
        "subtopics": []
    }
    
    # Find all subtopics - improved pattern to handle special characters
    # Match: \item [title text that may include \&, etc.] \begin{itemize}...\end{itemize}
    subtopic_pattern = r'\\item\s+([^\n]+?)\s*\\begin\{itemize\}(.*?)\\end\{itemize\}'
    subtopics = re.findall(subtopic_pattern, topic_content, re.DOTALL)
    
    for subtopic_title, subtopic_content in subtopics:
        subtopic_title_clean = clean_latex(subtopic_title)
        subtopic_id = subtopic_title_clean.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '').replace('&', 'and')
        
        # Extract papers from this subtopic
        paper_items = re.findall(r'\\item\s+(.*?)(?=\\item|$)', subtopic_content, re.DOTALL)
        
        papers = []
        for item_text in paper_items:
            # Extract title (in {\it ...} or {\bf ...})
            title_match = re.search(r'\{\\it\s+([^}]+)\}', item_text)
            if not title_match:
                title_match = re.search(r'\{\\bf\s+([^}]+)\}', item_text)
            
            if title_match:
                title = clean_latex(title_match.group(1))
                authors, venue, year = extract_authors_venue_year(item_text)
                paper_type = determine_paper_type(venue)
                pdf_link = find_pdf_link(title, html_content)
                
                # Check for awards
                award = None
                if 'ICAPS Influential Paper' in item_text or 'test-of-time' in item_text:
                    award = "ICAPS Influential Paper Award 2023"
                
                paper = {
                    "id": f"{topic_id}-{subtopic_id}-{len(papers) + 1}",
                    "title": title,
                    "authors": authors if authors else ["M. Katz"],
                    "venue": venue,
                    "year": year,
                    "type": paper_type,
                    "links": {},
                    "award": award
                }
                
                if pdf_link:
                    paper["links"]["pdf"] = pdf_link
                
                papers.append(paper)
        
        if papers:
            topic_entry["subtopics"].append({
                "id": subtopic_id,
                "title": subtopic_title_clean,
                "papers": papers
            })
    
    if topic_entry["subtopics"]:
        publications_data["topics"].append(topic_entry)

# Count total papers
total_papers = sum(
    len(paper)
    for topic in publications_data["topics"]
    for subtopic in topic["subtopics"]
    for paper in subtopic["papers"]
)
publications_data["metadata"]["totalPapers"] = total_papers

# Write to JSON
output_path = Path("data/publications.json")
output_path.parent.mkdir(exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(publications_data, f, indent=2, ensure_ascii=False)

print(f"Extracted {total_papers} papers from CV")
print(f"Output written to {output_path}")

# Print detailed summary
for topic in publications_data["topics"]:
    topic_total = sum(len(st["papers"]) for st in topic["subtopics"])
    print(f"\n{topic['title']}: {topic_total} papers")
    for subtopic in topic["subtopics"]:
        print(f"  - {subtopic['title']}: {len(subtopic['papers'])} papers")

print(f"\nExpected from CV: ~89-101 papers")
print(f"Extracted: {total_papers} papers")
if total_papers < 89:
    print(f"WARNING: Missing {89 - total_papers} papers!")

# Made with Bob
