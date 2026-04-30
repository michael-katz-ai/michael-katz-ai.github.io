#!/usr/bin/env python3
"""
CV LaTeX to JSONL Converter
Extracts publications from CV LaTeX file with category and subcategory metadata.
"""

import json
import re
import sys
from pathlib import Path


def clean_latex(text):
    """Remove LaTeX commands and clean up text."""
    # Handle math expressions first
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


def extract_title_from_item(item_text):
    """Extract title from {\it ...} handling nested braces."""
    start = item_text.find('{\\it')
    if start == -1:
        return None
    
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


def parse_cv_publications(cv_path):
    """
    Parse CV LaTeX file and extract publications with categories.
    
    Returns:
        List of dictionaries with publication data including category/subcategory
    """
    with open(cv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    publications = []
    current_category = None
    current_subcategory = None
    
    # Split into lines for processing
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for category (subsection)
        if line.startswith('\\subsection*{'):
            match = re.search(r'\\subsection\*\{([^}]+)\}', line)
            if match:
                current_category = match.group(1)
                current_subcategory = None
        
        # Check for subcategory (top-level \item before itemize, without {\bf or {\it)
        elif line.startswith('\\item ') and '{\\bf' not in line and '{\\it' not in line:
            # This might be a subcategory header
            # Check if next line is \begin{itemize}
            if i + 1 < len(lines) and '\\begin{itemize}' in lines[i + 1]:
                subcategory_text = line[6:].strip()  # Remove '\item '
                current_subcategory = clean_latex(subcategory_text)
        
        # Check for publication entry (starts with \item and will have {\it for title)
        elif line.startswith('\\item '):
            # Collect multi-line entry first
            entry_lines = [line]
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('\\item') and not lines[j].strip().startswith('\\end{itemize}') and not lines[j].strip().startswith('\\subsection'):
                entry_lines.append(lines[j])
                j += 1
            
            item_text = ' '.join(entry_lines)
            
            # Check if this is a publication entry (has {\it for title)
            if '{\\it' not in item_text:
                i += 1
                continue
            
            # Extract title
            title = extract_title_from_item(item_text)
            if not title:
                i += 1
                continue
            
            # Extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', item_text)
            year = int(year_match.group(0)) if year_match else None
            
            # Extract authors
            title_start = item_text.find('{\\it')
            authors = []
            if title_start > 0:
                author_text = item_text[:title_start]
                author_text = clean_latex(author_text)
                authors = [a.strip() for a in re.split(r',\s*|\s+and\s+', author_text) if a.strip() and len(a.strip()) > 2]
                authors = [a for a in authors if not any(x in a.lower() for x in ['proceedings', 'conference', 'journal'])]
                authors = [a.rstrip('.,') for a in authors]
            
            # Extract venue (after title, before year)
            venue = ""
            if title_start > 0:
                after_title = item_text[title_start:]
                # Find the closing brace of {\it ...}
                title_end = after_title.find('}')
                if title_end > 0:
                    remaining = after_title[title_end+1:].strip()
                    # Venue is between title and year
                    if year_match:
                        venue_text = remaining[:remaining.find(str(year))] if str(year) in remaining else remaining
                        venue = clean_latex(venue_text).strip(' ,.').strip()
            
            # Create publication entry
            pub = {
                'title': title,
                'authors': authors,
                'year': year,
                'venue': venue,
                'category': current_category,
                'subcategory': current_subcategory
            }
            
            publications.append(pub)
            i = j - 1
        
        i += 1
    
    return publications


def cv_to_jsonl(cv_path, output_path):
    """Convert CV LaTeX to JSONL format with categories."""
    print(f"Parsing CV from: {cv_path}")
    
    publications = parse_cv_publications(cv_path)
    
    print(f"Extracted {len(publications)} publications")
    
    # Count by category
    categories = {}
    for pub in publications:
        cat = pub.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nPublications by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Write JSONL
    with open(output_path, 'w', encoding='utf-8') as f:
        for pub in publications:
            json.dump(pub, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"\nWrote JSONL to: {output_path}")
    
    return len(publications)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert CV LaTeX to JSONL format with categories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract publications from CV
  python cv_to_jsonl.py /path/to/cv.tex cv_publications.jsonl
        """
    )
    
    parser.add_argument('cv_file', help='Input CV LaTeX file')
    parser.add_argument('output_file', help='Output JSONL file')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.cv_file).exists():
        print(f"Error: CV file not found: {args.cv_file}", file=sys.stderr)
        sys.exit(1)
    
    # Convert
    try:
        count = cv_to_jsonl(args.cv_file, args.output_file)
        print(f"\n✅ Successfully converted {count} publications to JSONL")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

