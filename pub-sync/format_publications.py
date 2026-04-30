#!/usr/bin/env python3
"""
Publication Formatters
Convert JSONL publication entries to different output formats:
- BibTeX format
- CV LaTeX format
- Website JSON format
"""

import json
import sys
from pathlib import Path


def format_bibtex_entry(pub):
    """
    Convert JSONL publication entry to BibTeX format.
    
    Args:
        pub: Dictionary with publication data
        
    Returns:
        String with BibTeX entry
    """
    entry_type = pub.get('type', 'inproceedings')
    entry_id = pub.get('id', 'unknown')
    
    lines = [f"@{entry_type.capitalize()}{{{entry_id},"]
    
    # Add fields in standard order
    field_order = [
        'author', 'title', 'booktitle', 'journal', 'year', 'month',
        'volume', 'number', 'pages', 'publisher', 'address',
        'editor', 'series', 'edition', 'chapter',
        'organization', 'school', 'institution', 'howpublished',
        'doi', 'url', 'note', 'crossref'
    ]
    
    for field in field_order:
        if field == 'author' and 'author_string' in pub:
            # Use original author string
            value = pub['author_string']
            lines.append(f'  author =       "{value}",')
        elif field in pub and pub[field]:
            value = pub[field]
            # Escape special characters
            value = str(value).replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'  {field} = "{value}",')
    
    # Remove trailing comma from last line
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]
    
    lines.append('}')
    
    return '\n'.join(lines)


def format_cv_latex_entry(pub):
    """
    Convert JSONL publication entry to CV LaTeX format.
    
    Args:
        pub: Dictionary with publication data
        
    Returns:
        String with LaTeX \item entry
    """
    # Format: \item Authors, {\it Title}, Venue, Year.
    
    authors = pub.get('author_string', '')
    # Bold the user's name (assuming Michael Katz)
    authors = authors.replace('Michael Katz', '{\\bf Michael Katz}')
    
    title = pub.get('title', '')
    year = pub.get('year', '')
    
    # Determine venue
    venue = pub.get('booktitle', pub.get('journal', ''))
    
    # Build the entry
    parts = []
    if authors:
        parts.append(authors)
    if title:
        parts.append(f"{{\\it {title}}}")
    if venue:
        parts.append(venue)
    if year:
        parts.append(str(year))
    
    entry = ', '.join(parts)
    if entry and not entry.endswith('.'):
        entry += '.'
    
    return f"\\item {entry}"


def format_website_json_entry(pub):
    """
    Convert JSONL publication entry to website JSON format.
    
    Args:
        pub: Dictionary with publication data
        
    Returns:
        Dictionary suitable for website JSON
    """
    # Extract year from string if needed
    year = pub.get('year', '')
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    
    # Build website entry
    entry = {
        'title': pub.get('title', ''),
        'authors': pub.get('authors', []),
        'venue': pub.get('booktitle', pub.get('journal', '')),
        'year': year,
        'type': determine_publication_type(pub),
    }
    
    # Add optional fields
    if 'doi' in pub:
        entry['doi'] = pub['doi']
    if 'url' in pub:
        entry['url'] = pub['url']
    if 'pages' in pub:
        entry['pages'] = pub['pages']
    
    # Try to construct PDF link
    pdf_link = construct_pdf_link(pub)
    if pdf_link:
        entry['pdf'] = pdf_link
    
    return entry


def determine_publication_type(pub):
    """Determine publication type for website."""
    entry_type = pub.get('type', '').lower()
    venue = pub.get('booktitle', pub.get('journal', '')).lower()
    
    if entry_type == 'article':
        return 'journal'
    elif 'workshop' in venue or 'ws' in pub.get('id', '').lower():
        return 'workshop'
    elif entry_type == 'inproceedings':
        return 'conference'
    elif entry_type == 'phdthesis':
        return 'thesis'
    elif entry_type == 'techreport':
        return 'technical_report'
    else:
        return 'other'


def construct_pdf_link(pub):
    """Construct PDF link from publication data."""
    # Try to build PDF link from ID
    entry_id = pub.get('id', '')
    if entry_id:
        # Common pattern: papers/id.pdf
        return f"papers/{entry_id}.pdf"
    return None


def jsonl_to_bibtex(input_file, output_file):
    """Convert JSONL file to BibTeX format."""
    entries = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            pub = json.loads(line)
            entry = format_bibtex_entry(pub)
            entries.append(entry)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(entries))
        f.write('\n')
    
    return len(entries)


def jsonl_to_cv_latex(input_file, output_file):
    """Convert JSONL file to CV LaTeX format."""
    entries = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            pub = json.loads(line)
            entry = format_cv_latex_entry(pub)
            entries.append(entry)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\\begin{itemize}[noitemsep]\n')
        for entry in entries:
            f.write(entry + '\n')
        f.write('\\end{itemize}\n')
    
    return len(entries)


def jsonl_to_website_json(input_file, output_file):
    """Convert JSONL file to website JSON format."""
    entries = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            pub = json.loads(line)
            entry = format_website_json_entry(pub)
            entries.append(entry)
    
    # Sort by year (descending), handling both int and string years
    def get_year(entry):
        year = entry.get('year', 0)
        if isinstance(year, str):
            return int(year) if year.isdigit() else 0
        return year if isinstance(year, int) else 0
    
    entries.sort(key=get_year, reverse=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return len(entries)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert JSONL publications to different formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to BibTeX
  python format_publications.py katz_pubs.jsonl output.bib --format bibtex
  
  # Convert to CV LaTeX
  python format_publications.py katz_pubs.jsonl cv_section.tex --format cv
  
  # Convert to website JSON
  python format_publications.py katz_pubs.jsonl publications.json --format web
        """
    )
    
    parser.add_argument('input_file', help='Input JSONL file')
    parser.add_argument('output_file', help='Output file')
    parser.add_argument('--format', choices=['bibtex', 'cv', 'web'], required=True,
                       help='Output format')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Convert
    try:
        if args.format == 'bibtex':
            count = jsonl_to_bibtex(args.input_file, args.output_file)
            print(f"✅ Converted {count} entries to BibTeX format")
        elif args.format == 'cv':
            count = jsonl_to_cv_latex(args.input_file, args.output_file)
            print(f"✅ Converted {count} entries to CV LaTeX format")
        elif args.format == 'web':
            count = jsonl_to_website_json(args.input_file, args.output_file)
            print(f"✅ Converted {count} entries to website JSON format")
        
        print(f"Output written to: {args.output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
