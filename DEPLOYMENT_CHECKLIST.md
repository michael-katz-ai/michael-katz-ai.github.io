# Website Deployment Checklist

## Overview
This document provides a complete checklist for deploying the new Michael Katz academic website to a different GitHub repository.

## Site Structure

### Core HTML Pages (7 pages)
- ✅ `index.html` - Home page with featured publications and awards
- ✅ `about.html` - Biography, education, awards, and activities
- ✅ `contact.html` - Contact information and collaboration opportunities
- ✅ `publications.html` - Complete publications list (102 papers)
- ✅ `research.html` - Research highlights, software, and patents
- ✅ `patents.html` - Granted and published patents (26 total)
- ✅ `collaborators.html` - List of 99 co-authors

### Assets & Resources

#### CSS (1 file)
- ✅ `css/styles.css` - Complete styling with responsive design

#### JavaScript (3 files)
- ✅ `js/main.js` - Navigation and UI interactions
- ✅ `js/publications.js` - Dynamic publications loading and filtering
- ✅ `js/collaborators.js` - Collaborators page functionality

#### Data Files (5 JSON files)
- ✅ `data/publications.json` - Main publications data (102 papers, 5 topics)
- ✅ `data/publications-full.json` - Chronological publications list
- ✅ `data/publications-complete.json` - Extended publication data
- ✅ `data/publications_reconciliation.json` - Cross-reference data
- ✅ `data/collaborators.json` - 99 co-authors with paper counts

#### Images (14 files)
- ✅ `images/mypic.jpg` - Profile photo
- ✅ `images/eyes.png` - Header graphic
- ✅ `images/fac_tel.png` - Contact icon
- ✅ `images/ieletter.png` - Email icon
- ✅ `images/iemail.png` - Email icon variant
- ✅ `images/ruleblue.gif` - Divider graphic
- ✅ `images/turnbook.gif` - Book icon
- ✅ `images/Images/*` - Duplicate image directory (can be cleaned up)

#### Papers (95+ PDF files)
- ✅ `papers/*.pdf` - All publication PDFs
- ✅ `papers/tmp-removed/` - Archived papers (3 files)

#### PhD Materials (3 files)
- ✅ `PHD/MichaelKatzPhD.pdf` - PhD thesis
- ✅ `PHD/PhDAwardICAPS-talk.pdf` - Award talk slides
- ✅ `PHD/Proposal.pdf` - PhD proposal

#### CV
- ✅ `CV_Michael_Katz.pdf` - Current CV

### Development & Documentation Files

#### Publication Sync Tools (`pub-sync/` directory)
- ✅ `pub-sync/README.md` - Documentation for publication system
- ✅ `pub-sync/bibtex_to_jsonl.py` - BibTeX parser
- ✅ `pub-sync/cv_to_jsonl.py` - CV LaTeX parser
- ✅ `pub-sync/merge_publications.py` - Merger tool
- ✅ `pub-sync/format_website_json_v2.py` - Website formatter
- ✅ `pub-sync/*.json` - Configuration files

#### Documentation
- ✅ `README.md` - Main documentation
- ✅ `PUBLICATIONS_JSON_GUIDE.md` - Publications system guide
- ✅ `PUBLICATIONS_RESTRUCTURE_PLAN.md` - Restructure documentation

#### Utility Scripts
- ✅ `serve.sh` - Local development server script

## Pre-Deployment Checklist

### 1. File Cleanup
- [ ] Remove development/analysis Python scripts from root
- [ ] Remove markdown documentation files (or move to docs/)
- [ ] Clean up `images/Images/` duplicate directory
- [ ] Remove `papers/tmp-removed/` if not needed
- [ ] Remove old `coauthors.html` (replaced by `collaborators.html`)

### 2. Content Verification
- [x] All 7 HTML pages have consistent headers
- [x] All 7 HTML pages have consistent footers with LinkedIn
- [x] All internal links use relative paths
- [x] All paper PDFs are accessible
- [x] Publications data is up to date (102 papers)
- [x] Collaborators data is current (99 co-authors)

### 3. Configuration Updates
- [ ] Update any hardcoded URLs to new GitHub Pages domain
- [ ] Verify all external links work
- [ ] Check social media links (Google Scholar, GitHub, LinkedIn, IBM Research)
- [ ] Update copyright year if needed (currently 2026)

### 4. Testing
- [ ] Test all navigation links
- [ ] Test publications filtering and search
- [ ] Test collapsible sections
- [ ] Test responsive design on mobile
- [ ] Verify all PDFs load correctly
- [ ] Test collaborators search functionality

## Deployment Steps

### Option 1: GitHub Pages (Recommended)

1. **Create New Repository**
   ```bash
   # On GitHub, create new repository (e.g., username.github.io)
   ```

2. **Copy Files**
   ```bash
   # Copy all files from new-site/ to new repository
   cd /path/to/new-repo
   cp -r /path/to/ctpelok77.github.io/new-site/* .
   ```

3. **Clean Up (Optional)**
   ```bash
   # Remove development files
   rm -rf pub-sync/
   rm *.py *.md (except README.md)
   rm -rf images/Images/  # Remove duplicate images
   ```

4. **Initialize Git**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Modern academic website"
   git branch -M main
   git remote add origin https://github.com/username/username.github.io.git
   git push -u origin main
   ```

5. **Enable GitHub Pages**
   - Go to repository Settings
   - Navigate to Pages section
   - Select "main" branch and "/" (root) folder
   - Save and wait for deployment

### Option 2: Custom Domain

1. Follow steps 1-4 from Option 1
2. Add `CNAME` file with your custom domain
3. Configure DNS settings with your domain provider
4. Enable HTTPS in GitHub Pages settings

## Post-Deployment Verification

- [ ] Visit the deployed site
- [ ] Test all pages load correctly
- [ ] Verify all links work
- [ ] Check mobile responsiveness
- [ ] Test publications search and filtering
- [ ] Verify PDF downloads work
- [ ] Check social media links
- [ ] Test contact form/email links

## Site Statistics

- **Total Pages**: 7 HTML pages
- **Publications**: 102 papers across 5 research topics
- **Patents**: 7 granted, 19 published applications
- **Collaborators**: 99 co-authors
- **PDF Files**: 95+ research papers + 3 PhD documents
- **Code**: ~2,500 lines of CSS/JS
- **Data**: 5 JSON files with structured content

## Key Features

1. **Responsive Design**: Mobile-first, works on all devices
2. **Dynamic Publications**: JavaScript-powered filtering and search
3. **Collapsible Sections**: All topics/subtopics start collapsed
4. **Modern UI**: Clean, professional design with smooth animations
5. **Consistent Navigation**: Same header/footer across all pages
6. **Social Integration**: Links to Google Scholar, GitHub, LinkedIn, IBM Research
7. **SEO Optimized**: Proper meta tags and semantic HTML
8. **Accessible**: ARIA labels and keyboard navigation support

## Maintenance

### Updating Publications
1. Update BibTeX file
2. Run `pub-sync/bibtex_to_jsonl.py`
3. Run `pub-sync/merge_publications.py`
4. Run `pub-sync/format_website_json_v2.py`
5. Copy updated `publications.json` to `data/`
6. Commit and push changes

### Adding New Papers
1. Add PDF to `papers/` directory
2. Add entry to BibTeX file
3. Follow "Updating Publications" steps above

### Updating Collaborators
1. Export DBLP XML
2. Run collaborators extraction script
3. Update `data/collaborators.json`
4. Commit and push changes

## Support Files to Keep

**Essential for deployment:**
- All HTML, CSS, JS files
- All data JSON files
- All images
- All PDFs
- CV file
- README.md

**Optional (for maintenance):**
- `pub-sync/` directory (if you want to update publications)
- Development scripts (if you want to regenerate data)
- Documentation markdown files

**Can be removed:**
- Python analysis scripts in root
- Temporary/backup files
- Old coauthors.html

## Contact Information in Site

- **Email**: Michael.Katz1@ibm.com
- **Google Scholar**: https://scholar.google.com/citations?user=pltkfcMAAAAJ&hl=en
- **GitHub**: https://github.com/ctpelok77/
- **LinkedIn**: https://www.linkedin.com/in/michael-katz-5b5b2b1b/
- **IBM Research**: https://researcher.watson.ibm.com/researcher/view.php?person=ibm-Michael.Katz1

## Notes

- Site uses no external dependencies (no CDN links)
- All resources are self-contained
- Works offline once loaded
- No backend required
- Static site, perfect for GitHub Pages
- Fast loading times
- SEO friendly

---

**Last Updated**: April 30, 2026
**Version**: 1.0
**Status**: Ready for deployment