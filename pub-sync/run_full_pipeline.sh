#!/bin/bash
# Full publication extraction and formatting pipeline
# This script runs all steps from BibTeX extraction to final website JSON generation

set -e  # Exit on any error

# Configuration - set BibTeX directory
BIB_DIR="${1:-../../../../LaTeX/papers-shared/bib-ctpelok}"  # Default BibTeX directory
CV_PATH="${2:-../../../../LaTeX/papers-old/cv/chatgpt-cv.tex}"  # Default CV path (.tex file)

echo "=========================================="
echo "Publication Extraction Pipeline"
echo "=========================================="
echo ""
echo "BibTeX directory: $BIB_DIR"
echo "CV path: $CV_PATH"
echo ""

# Validate BibTeX files exist
if [ ! -f "$BIB_DIR/literatur.bib" ]; then
    echo "Error: literatur.bib not found in $BIB_DIR"
    exit 1
fi

# Step 1: Extract from BibTeX
echo "Step 1: Extracting publications from BibTeX..."
python3 bibtex_to_jsonl.py "$BIB_DIR/literatur.bib" katz_bibtex.jsonl \
    --abbrv "$BIB_DIR/abbrv.bib" \
    --crossref "$BIB_DIR/crossref.bib" \
    --author "Michael Katz"
echo "✓ BibTeX extraction complete"
echo ""

# Step 2: Extract from CV
echo "Step 2: Extracting publications from CV..."
python3 cv_to_jsonl.py "$CV_PATH" katz_cv.jsonl
echo "✓ CV extraction complete"
echo ""

# Step 3: Merge BibTeX and CV data
echo "Step 3: Merging BibTeX and CV data..."
python3 merge_bibtex_cv.py katz_bibtex.jsonl katz_cv.jsonl katz_unified.jsonl
echo "✓ Merge complete"
echo ""

# Step 4: Deduplicate publications
echo "Step 4: Deduplicating publications..."
python3 deduplicate_publications.py katz_unified.jsonl katz_unified_deduplicated.jsonl
echo "✓ Deduplication complete"
echo ""

# Step 5: Apply uncategorized resolution
echo "Step 5: Applying categorization to uncategorized publications..."
python3 apply_uncategorized_resolution.py katz_unified_deduplicated.jsonl uncategorized_resolution.json katz_unified_categorized.jsonl
echo "✓ Categorization complete"
echo ""

# Step 6: Generate paper order configuration (only if it doesn't exist)
if [ ! -f paper_order.json ]; then
    echo "Step 6: Generating paper order configuration (first time)..."
    python3 generate_paper_order.py katz_unified_categorized.jsonl paper_order.json
    echo "✓ Paper order configuration generated"
    echo ""
    echo "NOTE: paper_order.json created. Edit this file to customize paper order."
    echo "      It will be preserved on subsequent runs."
    echo ""
else
    echo "Step 6: Using existing paper_order.json (preserving your custom order)"
    echo ""
fi

# Step 7: Format for website
echo "Step 7: Formatting publications for website..."
python3 format_website_json_v2.py katz_unified_categorized.jsonl ../data/publications.json
echo "✓ Website JSON generated"
echo ""

echo "=========================================="
echo "Pipeline Complete!"
echo "=========================================="
echo ""
echo "Output files:"
echo "  - katz_bibtex.jsonl: Publications from BibTeX"
echo "  - katz_cv.jsonl: Publications from CV"
echo "  - katz_unified.jsonl: Merged publications"
echo "  - katz_unified_deduplicated.jsonl: Deduplicated publications"
echo "  - katz_unified_categorized.jsonl: Categorized publications"
echo "  - paper_order.json: Paper order configuration (edit to reorder)"
echo "  - ../data/publications.json: Final website JSON"
echo ""
echo "To reorder papers:"
echo "  1. Edit paper_order.json"
echo "  2. Run: python3 format_website_json_v2.py katz_unified_categorized.jsonl ../data/publications.json"
echo ""
echo "To view the website:"
echo "  cd .. && bash serve.sh"
echo ""
echo "Usage for next run:"
echo "  ./run_full_pipeline.sh [BIB_DIR] [CV_PATH]"
echo "  Default: ./run_full_pipeline.sh ../../bib ../../CV_Michael_Katz.tex"

# Made with Bob
