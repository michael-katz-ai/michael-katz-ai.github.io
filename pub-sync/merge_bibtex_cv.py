#!/usr/bin/env python3
"""
Merge BibTeX and CV JSONL files
Creates unified JSONL with BibTeX data enriched with CV categories.
"""

import json
import re
import sys
from pathlib import Path


def normalize_title(title):
    """Normalize title for matching."""
    if not title:
        return ""
    
    # Remove LaTeX commands and special characters
    title = title.replace(r'$^{\ast}$', '*')
    title = title.replace(r'$^\ast$', '*')
    title = title.replace(r'$^{*}$', '*')
    title = title.replace(r'$*$', '*')
    
    # Remove LaTeX formatting commands (e.g., \em, \bf, \it, \textbf{}, etc.)
    title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)  # \command{text} -> text
    title = re.sub(r'\\[a-zA-Z]+\s+', ' ', title)  # \command -> space
    title = re.sub(r'\\[a-zA-Z]+', '', title)  # \command -> nothing
    
    # Remove punctuation and make lowercase
    title = re.sub(r'[^\w\s]', '', title.lower())
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Remove leading articles (a, an, the)
    title = re.sub(r'^(a|an|the)\s+', '', title)
    
    return title


def load_jsonl(filepath):
    """Load JSONL file into list of dictionaries."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def create_title_index(entries):
    """Create index of entries by normalized title."""
    index = {}
    for entry in entries:
        title = entry.get('title', '')
        norm_title = normalize_title(title)
        if norm_title:
            index[norm_title] = entry
    return index


def merge_bibtex_cv(bibtex_jsonl, cv_jsonl, output_jsonl, author_filter=None):
    """
    Merge BibTeX and CV JSONL files.
    
    Args:
        bibtex_jsonl: Path to BibTeX JSONL file (authoritative source)
        cv_jsonl: Path to CV JSONL file (contains categories)
        output_jsonl: Path to output merged JSONL file
        author_filter: Optional author name to filter by
    """
    print(f"Loading BibTeX from: {bibtex_jsonl}")
    bibtex_entries = load_jsonl(bibtex_jsonl)
    print(f"  Loaded {len(bibtex_entries)} BibTeX entries")
    
    print(f"Loading CV from: {cv_jsonl}")
    cv_entries = load_jsonl(cv_jsonl)
    print(f"  Loaded {len(cv_entries)} CV entries")
    
    # Create title index for CV entries
    cv_index = create_title_index(cv_entries)
    print(f"  Indexed {len(cv_index)} CV entries by title")
    
    # Merge: start with BibTeX, add categories from CV
    merged = []
    matched_count = 0
    unmatched_count = 0
    
    for bib_entry in bibtex_entries:
        # Filter by author if specified
        if author_filter:
            author_string = bib_entry.get('author_string', '').lower()
            if author_filter.lower() not in author_string:
                continue
        
        # Try to find matching CV entry
        title = bib_entry.get('title', '')
        norm_title = normalize_title(title)
        
        cv_entry = cv_index.get(norm_title)
        
        if cv_entry:
            # Merge: BibTeX data + CV categories
            merged_entry = bib_entry.copy()
            merged_entry['category'] = cv_entry.get('category')
            merged_entry['subcategory'] = cv_entry.get('subcategory')
            merged.append(merged_entry)
            matched_count += 1
        else:
            # No CV match, include BibTeX entry without categories
            merged_entry = bib_entry.copy()
            merged_entry['category'] = None
            merged_entry['subcategory'] = None
            merged.append(merged_entry)
            unmatched_count += 1
    
    print(f"\nMerge results:")
    print(f"  Matched with CV: {matched_count}")
    print(f"  No CV match: {unmatched_count}")
    print(f"  Total merged: {len(merged)}")
    
    # Count by category
    categories = {}
    for entry in merged:
        cat = entry.get('category') or 'Uncategorized'
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nPublications by category:")
    for cat, count in sorted(categories.items(), key=lambda x: (x[0] == 'Uncategorized', x[0])):
        print(f"  {cat}: {count}")
    
    # Write merged JSONL
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for entry in merged:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"\nWrote merged JSONL to: {output_jsonl}")
    
    return len(merged)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Merge BibTeX and CV JSONL files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge all entries
  python merge_bibtex_cv.py publications.jsonl cv_with_categories.jsonl merged.jsonl
  
  # Merge only Michael Katz publications
  python merge_bibtex_cv.py publications.jsonl cv_with_categories.jsonl katz_merged.jsonl --author "Michael Katz"
        """
    )
    
    parser.add_argument('bibtex_jsonl', help='Input BibTeX JSONL file (authoritative source)')
    parser.add_argument('cv_jsonl', help='Input CV JSONL file (contains categories)')
    parser.add_argument('output_jsonl', help='Output merged JSONL file')
    parser.add_argument('--author', help='Filter by author name')
    
    args = parser.parse_args()
    
    # Validate input files
    for filepath in [args.bibtex_jsonl, args.cv_jsonl]:
        if not Path(filepath).exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
    
    # Merge
    try:
        count = merge_bibtex_cv(
            args.bibtex_jsonl,
            args.cv_jsonl,
            args.output_jsonl,
            args.author
        )
        print(f"\n✅ Successfully merged {count} publications")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
