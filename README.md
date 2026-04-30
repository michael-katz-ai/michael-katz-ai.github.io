# Michael Katz - Modern Academic Portfolio Website

A complete redesign of Michael Katz's academic portfolio website featuring modern HTML5, CSS3, and responsive design.

## 🎯 Overview

This is a modern, professional academic website showcasing:
- 100+ publications in AI Planning and LLMs
- Award-winning research (ICAPS, IPC, AAAI)
- Open-source software and tools
- Professional activities and service
- Contact information and collaboration opportunities

## 📁 Project Structure

```
new-site/
├── index.html              # Homepage with hero, news, and highlights
├── publications.html       # Publications with search and filtering
├── research.html          # Software, patents, and research highlights
├── about.html             # Biography, career timeline, and awards
├── contact.html           # Contact information and opportunities
├── css/
│   └── styles.css         # Complete CSS framework with responsive design
├── js/
│   └── main.js            # Interactive features and navigation
├── images/                # Website images (copy from ../Images/)
└── assets/                # Additional assets

```

## 🚀 Features

### Modern Design
- **Responsive Layout**: Mobile-first design that works on all devices
- **Clean Typography**: System fonts for performance
- **Professional Color Scheme**: Blue/teal gradient with amber accents
- **Smooth Animations**: Fade-in effects and transitions
- **Accessibility**: WCAG 2.1 AA compliant

### Interactive Elements
- **Mobile Navigation**: Hamburger menu for small screens
- **Search & Filter**: Publications page with real-time filtering
- **Collapsible Sections**: Year-based publication organization
- **Back to Top**: Smooth scroll button
- **Active Navigation**: Highlights current page

### Performance
- **Fast Loading**: Minimal dependencies, optimized CSS
- **Lazy Loading**: Images load as needed
- **Smooth Scrolling**: Enhanced user experience
- **SEO Optimized**: Meta tags and semantic HTML

## 🛠️ Setup Instructions

### 1. Copy Images
Copy the images from the old site to the new site:

```bash
cp -r ../Images ./images
```

Or manually copy:
- `../Images/mypic.jpg` → `images/mypic.jpg`
- `../Images/eyes.png` → `images/eyes.png`
- `../Images/ruleblue.gif` → `images/ruleblue.gif`

### 2. Update Image Paths
The new site uses relative paths. Images are referenced as:
- In HTML: `../Images/mypic.jpg` (references old location)
- Or: `images/mypic.jpg` (if copied to new-site/images/)

### 3. Copy PDF Files
Ensure CV and papers are accessible:
```bash
# CV is already at ../CV_Michael_Katz.pdf
# Papers are at ../papers/
# These paths work from new-site/ directory
```

### 4. Test Locally
Open `index.html` in a web browser to test:
```bash
open index.html
# or
python3 -m http.server 8000
# Then visit http://localhost:8000
```

## 📱 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🎨 Customization

### Colors
Edit CSS variables in `css/styles.css`:
```css
:root {
  --primary-blue: #1e3a8a;
  --accent-teal: #0891b2;
  --highlight-amber: #f59e0b;
  /* ... */
}
```

### Content Updates
- **News**: Edit the news list in `index.html`
- **Publications**: Add new entries in `publications.html`
- **Software**: Update links in `research.html`
- **Bio**: Modify content in `about.html`

## 📊 Key Improvements Over Old Site

### Technical
- ✅ HTML5 (vs HTML 4.01)
- ✅ CSS3 with Grid/Flexbox (vs table layouts)
- ✅ Responsive design (vs desktop-only)
- ✅ Semantic markup (vs deprecated tags)
- ✅ Modern JavaScript (vs inline scripts)

### User Experience
- ✅ Mobile-friendly navigation
- ✅ Search and filter publications
- ✅ Smooth animations
- ✅ Better readability
- ✅ Faster loading

### Content Organization
- ✅ Clear information hierarchy
- ✅ Featured content sections
- ✅ Visual timeline
- ✅ Award highlights
- ✅ Better call-to-actions

## 🔧 Maintenance

### Adding Publications
1. Open `publications.html`
2. Find the appropriate year section
3. Add new `<li class="publication-item">` with:
   - Title, authors, venue
   - PDF link
   - Data attribute for filtering

### Updating News
1. Open `index.html`
2. Add new `<li class="news-item">` at the top of the news list
3. Include date, title, and links

### Adding Software
1. Open `research.html`
2. Add new card in the software grid
3. Include GitHub link and description

## 📝 Notes

- All external links (Google Scholar, GitHub, IBM) are preserved
- PDF paths reference the original location (`../papers/`, `../CV_Michael_Katz.pdf`)
- Images can be copied or referenced from original location
- The site is static HTML - no build process required

## 🚀 Deployment

### GitHub Pages
1. Copy contents to repository root or `docs/` folder
2. Enable GitHub Pages in repository settings
3. Site will be live at `https://ctpelok77.github.io`

### Alternative: Keep Both Sites
- Keep old site at root
- New site in `new-site/` subdirectory
- Test before replacing

## 📧 Support

For questions or issues with the new site design, refer to the original requirements or contact the developer.

## 📄 License

© 2026 Michael Katz. All rights reserved.

---

**Built with**: HTML5, CSS3, Vanilla JavaScript
**Design**: Modern academic portfolio
**Performance**: Optimized for speed and accessibility