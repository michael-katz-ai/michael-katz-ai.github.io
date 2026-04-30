#!/usr/bin/env python3
"""
BibTeX to JSONL Converter
Parses BibTeX database and outputs JSONL format (one JSON object per line).
Each line represents a single publication with all its metadata.
"""

import json
import sys
from pathlib import Path
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode


def clean_field(value):
    """Clean BibTeX field value."""
    if not value:
        return ""
    
    # Remove extra whitespace and newlines
    value = ' '.join(value.split())
    
    # Remove LaTeX commands (basic cleanup)
    import re
    value = re.sub(r'\\textbf\{([^}]*)\}', r'\1', value)
    value = re.sub(r'\\textit\{([^}]*)\}', r'\1', value)
    value = re.sub(r'\\emph\{([^}]*)\}', r'\1', value)
    value = re.sub(r'\{\\it\s+([^}]*)\}', r'\1', value)
    value = re.sub(r'\{\\bf\s+([^}]*)\}', r'\1', value)
    value = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', value)
    
    # Handle common LaTeX escapes
    value = value.replace(r'\&', '&')
    value = value.replace(r'\_', '_')
    value = value.replace(r'\%', '%')
    value = value.replace(r'\$', '$')
    
    # Remove remaining braces
    value = value.replace('{', '').replace('}', '')
    
    return value.strip()


def parse_authors(author_string):
    """Parse author string into list of author names."""
    if not author_string:
        return []
    
    # Split by 'and'
    authors = [a.strip() for a in author_string.split(' and ')]
    
    # Clean each author name
    authors = [clean_field(a) for a in authors if a.strip()]
    
    return authors


def entry_to_dict(entry, strings_dict, crossref_entries):
    """Convert BibTeX entry to dictionary with resolved crossrefs and strings."""
    result = {
        'id': entry.get('ID', ''),
        'type': entry.get('ENTRYTYPE', ''),
    }
    
    # Standard fields
    fields_to_extract = [
        'title', 'author', 'year', 'month', 'journal', 'booktitle',
        'volume', 'number', 'pages', 'publisher', 'address',
        'doi', 'url', 'note', 'abstract', 'keywords',
        'editor', 'series', 'edition', 'chapter', 'organization',
        'school', 'institution', 'howpublished'
    ]
    
    for field in fields_to_extract:
        if field in entry:
            value = entry[field]
            
            # Resolve string abbreviations
            if value in strings_dict:
                value = strings_dict[value]
            
            # Special handling for authors
            if field == 'author':
                result['authors'] = parse_authors(value)
                result['author_string'] = clean_field(value)
            else:
                result[field] = clean_field(value)
    
    # Handle crossref - resolve to get booktitle/journal
    if 'crossref' in entry:
        crossref_id = entry['crossref']
        result['crossref'] = crossref_id
        
        # Try to resolve crossref to get venue information
        if crossref_id in crossref_entries:
            crossref_entry = crossref_entries[crossref_id]
            # Get booktitle or title from crossref entry
            if 'booktitle' in crossref_entry and 'booktitle' not in result:
                result['booktitle'] = clean_field(crossref_entry['booktitle'])
            elif 'title' in crossref_entry and 'booktitle' not in result:
                result['booktitle'] = clean_field(crossref_entry['title'])
            # Get year if not present
            if 'year' in crossref_entry and 'year' not in result:
                result['year'] = clean_field(crossref_entry['year'])
    
    # Add raw entry for reference
    result['bibtex_key'] = entry.get('ID', '')
    
    return result


def load_bibtex(bib_path, abbrv_path=None, crossref_path=None):
    """Load BibTeX file with optional abbreviations and crossref files."""
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    parser.customization = convert_to_unicode
    parser.expect_multiple_parse = True
    
    # Load abbreviations first
    strings_dict = {}
    if abbrv_path and Path(abbrv_path).exists():
        with open(abbrv_path, 'r', encoding='utf-8') as f:
            abbrv_db = bibtexparser.load(f, parser=parser)
            strings_dict = abbrv_db.strings
    
    # Load crossref file if provided
    if crossref_path and Path(crossref_path).exists():
        with open(crossref_path, 'r', encoding='utf-8') as f:
            crossref_db = bibtexparser.load(f, parser=parser)
    
    # Load main BibTeX file
    with open(bib_path, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f, parser=parser)
        
        # Merge strings
        if strings_dict:
            bib_database.strings.update(strings_dict)
    
    return bib_database, bib_database.strings


def bibtex_to_jsonl(bib_path, output_path, abbrv_path=None, crossref_path=None, exclude_types=None, filter_author=None):
    """
    Convert BibTeX to JSONL format.
    
    Args:
        bib_path: Path to BibTeX file
        output_path: Path to output JSONL file
        abbrv_path: Optional path to abbreviations file
        crossref_path: Optional path to crossref file
        exclude_types: Optional list of entry types to exclude (e.g., ['misc'])
        filter_author: Optional author name to filter by (case-insensitive substring match)
    """
    if exclude_types is None:
        exclude_types = []
    
    print(f"Loading BibTeX from: {bib_path}")
    if abbrv_path:
        print(f"Loading abbreviations from: {abbrv_path}")
    if crossref_path:
        print(f"Loading crossrefs from: {crossref_path}")
    if filter_author:
        print(f"Filtering by author: {filter_author}")
    
    bib_database, strings_dict = load_bibtex(bib_path, abbrv_path, crossref_path)
    
    print(f"Found {len(bib_database.entries)} entries")
    
    # Build crossref lookup dictionary
    crossref_entries = {}
    for entry in bib_database.entries:
        entry_id = entry.get('ID', '')
        entry_type = entry.get('ENTRYTYPE', '').lower()
        # Store proceedings, books, etc. that might be crossreferenced
        if entry_type in ['proceedings', 'book', 'incollection', 'inbook']:
            crossref_entries[entry_id] = entry
    
    print(f"Found {len(crossref_entries)} crossref entries")
    
    # Convert entries to dictionaries
    entries = []
    excluded_count = 0
    filtered_count = 0
    
    for entry in bib_database.entries:
        entry_type = entry.get('ENTRYTYPE', '').lower()
        entry_id = entry.get('ID', '')
        
        # Exclude crossref-only entries (proceedings, books that are only used for crossreferencing)
        # These are entries that other entries reference via crossref field
        if entry_type in ['proceedings', 'book'] and entry_id in crossref_entries:
            # Check if this entry has an author field - if not, it's likely just a crossref entry
            if 'author' not in entry and 'editor' not in entry:
                excluded_count += 1
                continue
        
        # Check if entry should be excluded by type
        if entry_type in exclude_types:
            excluded_count += 1
            continue
        
        # Check if this is a Zenodo entry (misc with zenodo in howpublished)
        if entry_type == 'misc':
            howpublished = entry.get('howpublished', '').lower()
            if 'zenodo' in howpublished:
                excluded_count += 1
                continue
        
        entry_dict = entry_to_dict(entry, strings_dict, crossref_entries)
        
        # Check if entry should be filtered by author
        if filter_author:
            author_string = entry_dict.get('author_string', '').lower()
            if filter_author.lower() not in author_string:
                filtered_count += 1
                continue
        
        entries.append(entry_dict)
    
    print(f"Converted {len(entries)} entries")
    if excluded_count > 0:
        print(f"Excluded {excluded_count} entries of types: {exclude_types}")
    if filtered_count > 0:
        print(f"Filtered out {filtered_count} entries not matching author: {filter_author}")
    
    # Write JSONL
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"Wrote JSONL to: {output_path}")
    
    return len(entries)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert BibTeX to JSONL format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  python bibtex_to_jsonl.py literatur.bib publications.jsonl
  
  # With abbreviations file
  python bibtex_to_jsonl.py literatur.bib publications.jsonl --abbrv abbrv.bib
  
  # Exclude Zenodo entries (misc type)
  python bibtex_to_jsonl.py literatur.bib publications.jsonl --exclude misc
  
  # Filter by author (case-insensitive substring match)
  python bibtex_to_jsonl.py literatur.bib katz_pubs.jsonl --author "Michael Katz"
  
  # Combine filters
  python bibtex_to_jsonl.py literatur.bib katz_pubs.jsonl --author "Katz" --exclude misc
        """
    )
    
    parser.add_argument('bib_file', help='Input BibTeX file')
    parser.add_argument('output_file', help='Output JSONL file')
    parser.add_argument('--abbrv', help='Abbreviations BibTeX file')
    parser.add_argument('--crossref', help='Crossref BibTeX file')
    parser.add_argument('--exclude', nargs='+', help='Entry types to exclude (e.g., misc)')
    parser.add_argument('--author', help='Filter by author name (case-insensitive substring match)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.bib_file).exists():
        print(f"Error: BibTeX file not found: {args.bib_file}", file=sys.stderr)
        sys.exit(1)
    
    # Convert
    try:
        count = bibtex_to_jsonl(
            args.bib_file,
            args.output_file,
            abbrv_path=args.abbrv,
            crossref_path=args.crossref,
            exclude_types=args.exclude,
            filter_author=args.author
        )
        print(f"\n✅ Successfully converted {count} entries to JSONL")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
