#!/usr/bin/env python3
"""
CV LaTeX to JSONL Converter - Version 2
Simpler, more robust extraction using regex patterns.
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


def extract_title_with_braces(text, start_pos):
    """Extract title from {\it ...} handling nested braces."""
    pos = start_pos + 4  # len('{\\it')
    brace_count = 1
    title_start = pos
    
    while pos < len(text) and brace_count > 0:
        if text[pos] == '{':
            brace_count += 1
        elif text[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count == 0:
        title = text[title_start:pos-1].strip()
        return clean_latex(title), pos
    return None, start_pos


def parse_cv_publications(cv_path):
    """Parse CV LaTeX file and extract publications with categories."""
    with open(cv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    publications = []
    current_category = None
    current_subcategory = None
    
    # Find all subsections (categories)
    category_pattern = r'\\subsection\*\{([^}]+)\}'
    categories = [(m.start(), m.group(1)) for m in re.finditer(category_pattern, content)]
    
    # Find all \item entries with {\it titles (publications)
    # Pattern: \item followed by text containing {\it ...}
    item_pattern = r'\\item\s+([^\n]+(?:\n(?!\s*\\item|\s*\\end\{itemize\}|\s*\\subsection)[^\n]+)*)'
    
    for match in re.finditer(item_pattern, content, re.MULTILINE):
        item_text = match.group(1)
        item_pos = match.start()
        
        # Check if this item contains {\it (title marker)
        if '{\\it' not in item_text:
            continue
        
        # Determine current category based on position
        current_category = None
        for cat_pos, cat_name in categories:
            if cat_pos < item_pos:
                current_category = cat_name
            else:
                break
        
        # Extract title
        title_start = item_text.find('{\\it')
        if title_start == -1:
            continue
        
        title, title_end_pos = extract_title_with_braces(item_text, title_start)
        if not title:
            continue
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', item_text)
        year = int(year_match.group(0)) if year_match else None
        
        # Extract authors (before title)
        author_text = item_text[:title_start]
        author_text = clean_latex(author_text)
        authors = [a.strip() for a in re.split(r',\s*|\s+and\s+', author_text) if a.strip() and len(a.strip()) > 2]
        authors = [a for a in authors if not any(x in a.lower() for x in ['proceedings', 'conference', 'journal'])]
        authors = [a.rstrip('.,') for a in authors]
        
        # Extract venue (after title, before year)
        venue = ""
        after_title = item_text[title_start + title_end_pos:]
        if year_match:
            venue_text = after_title[:after_title.find(str(year))] if str(year) in after_title else ""
            venue = clean_latex(venue_text).strip(' ,.').strip()
        
        # Try to determine subcategory
        # Look backwards from this position to find the last \item BEFORE \begin{itemize}
        before_text = content[:item_pos]
        # Find the last \begin{itemize} before this item
        last_itemize = before_text.rfind('\\begin{itemize}')
        if last_itemize > 0:
            # Look for \item BEFORE that \begin{itemize} (subcategory heading)
            before_itemize = before_text[:last_itemize]
            # Find the last \item before the \begin{itemize}
            subcat_match = None
            for match in re.finditer(r'\\item\s+([^\n\\]+)', before_itemize):
                subcat_match = match
            
            if subcat_match:
                potential_subcat = clean_latex(subcat_match.group(1))
                # Check if it's a subcategory (not a publication - should not have {\it)
                if '{\\it' not in subcat_match.group(0) and len(potential_subcat) > 0:
                    current_subcategory = potential_subcat
        
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
    
    return publications


def cv_to_jsonl(cv_path, output_path):
    """Convert CV LaTeX to JSONL format with categories."""
    print(f"Parsing CV from: {cv_path}")
    
    publications = parse_cv_publications(cv_path)
    
    print(f"Extracted {len(publications)} publications")
    
    # Count by category
    categories = {}
    for pub in publications:
        cat = pub.get('category') or 'Unknown'
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nPublications by category:")
    for cat, count in sorted(categories.items(), key=lambda x: (x[0] is None, x[0])):
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
        description='Convert CV LaTeX to JSONL format with categories (v2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract publications from CV
  python cv_to_jsonl_v2.py /path/to/cv.tex cv_publications.jsonl
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
