/**
 * Publications Manager
 * Handles loading, filtering, and rendering of publications from JSON data
 */

class PublicationsManager {
    constructor() {
        this.data = null;
        this.currentFilter = 'all';
        this.searchTerm = '';
    }

    /**
     * Load publications data from JSON file
     */
    async loadData() {
        try {
            const response = await fetch('data/publications.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.data = await response.json();
            return this.data;
        } catch (error) {
            console.error('Error loading publications data:', error);
            console.error('Error details:', {
                message: error.message,
                type: error.name,
                stack: error.stack
            });
            throw error;
        }
    }

    /**
     * Initialize the publications page
     */
    async init() {
        await this.loadData();
        this.renderThesis();
        this.renderTopics();
        this.setupEventListeners();
        this.updateStats();
    }

    /**
     * Render PhD thesis section
     */
    renderThesis() {
        const thesis = this.data.thesis;
        const thesisSection = document.getElementById('thesis-section');
        
        if (!thesisSection) return;

        thesisSection.innerHTML = `
            <div class="card" style="border-left: 4px solid var(--highlight-amber);">
                <h3 style="color: var(--primary-blue); margin-bottom: 1rem;">🎓 PhD Thesis</h3>
                <h4 class="pub-title">${thesis.title}</h4>
                <p class="pub-venue">${thesis.university}, ${thesis.year}</p>
                <p style="margin: 1rem 0;"><strong>🏆 ${thesis.award}</strong></p>
                <div class="pub-links">
                    <a href="${thesis.links.pdf}" class="pub-link">📄 Full Thesis</a>
                    <a href="${thesis.links.slides}" class="pub-link">📊 Award Talk Slides</a>
                </div>
            </div>
        `;
    }

    /**
     * Render all topics and their publications
     */
    renderTopics() {
        const container = document.getElementById('publications-container');
        if (!container) return;

        container.innerHTML = '';

        this.data.topics.forEach(topic => {
            const topicElement = this.createTopicElement(topic);
            container.appendChild(topicElement);
        });
    }

    /**
     * Create a topic section element
     */
    createTopicElement(topic) {
        const section = document.createElement('div');
        section.className = 'topic-section';
        section.dataset.topicId = topic.id;

        // Count total papers in this topic
        const totalPapers = topic.subtopics.reduce((sum, subtopic) => 
            sum + subtopic.papers.length, 0);

        section.innerHTML = `
            <div class="topic-header">
                <div>
                    <h3>${topic.title}</h3>
                    <p class="topic-description">${topic.description}</p>
                    <span class="paper-count">${totalPapers} paper${totalPapers !== 1 ? 's' : ''}</span>
                </div>
                <span class="topic-toggle">▶</span>
            </div>
            <div class="topic-content collapsed">
                ${topic.subtopics.map(subtopic => this.createSubtopicHTML(subtopic)).join('')}
            </div>
        `;

        return section;
    }

    /**
     * Create HTML for a subtopic
     */
    createSubtopicHTML(subtopic) {
        if (subtopic.papers.length === 0) {
            return ''; // Don't show empty subtopics
        }

        const paperCount = subtopic.papers.length;
        
        return `
            <div class="subtopic-section">
                <div class="subtopic-header">
                    <h4 class="subtopic-title">${subtopic.title}</h4>
                    <span class="subtopic-count">${paperCount} paper${paperCount !== 1 ? 's' : ''}</span>
                    <span class="subtopic-toggle">▶</span>
                </div>
                <ul class="publications-list collapsed">
                    ${subtopic.papers.map(paper => this.createPaperHTML(paper)).join('')}
                </ul>
            </div>
        `;
    }

    /**
     * Create HTML for a single paper
     */
    createPaperHTML(paper) {
        const awardBadge = paper.award ? 
            `<p style="margin: 0.5rem 0; color: var(--highlight-amber); font-weight: 600;">🏆 ${paper.award}</p>` : '';
        
        const links = Object.entries(paper.links || {})
            .map(([type, url]) => {
                const icon = type === 'pdf' ? '📄' : 
                           type === 'slides' ? '📊' : 
                           type === 'code' ? '💻' : '🔗';
                return `<a href="${url}" class="pub-link">${icon} ${type.toUpperCase()}</a>`;
            })
            .join('');

        const borderStyle = paper.award ? 'style="border-left-color: var(--highlight-amber);"' : '';

        return `
            <li class="publication-item" data-type="${paper.type}" data-year="${paper.year}"
                data-venue="${paper.venue.toLowerCase()}" ${borderStyle}>
                <h4 class="pub-title">${paper.title}</h4>
                <p class="pub-authors">${paper.authors.join(', ')}</p>
                <p class="pub-venue">${paper.venue}, ${paper.year}</p>
                ${awardBadge}
                <div class="pub-links">
                    ${links}
                </div>
            </li>
        `;
    }

    /**
     * Setup event listeners for search and filtering
     */
    setupEventListeners() {
        // Topic toggle functionality
        document.querySelectorAll('.topic-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const section = e.currentTarget.closest('.topic-section');
                const content = section.querySelector('.topic-content');
                const toggle = section.querySelector('.topic-toggle');
                
                content.classList.toggle('collapsed');
                toggle.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
            });
        });

        // Subtopic toggle functionality
        document.querySelectorAll('.subtopic-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const section = e.currentTarget.closest('.subtopic-section');
                const list = section.querySelector('.publications-list');
                const toggle = section.querySelector('.subtopic-toggle');
                
                list.classList.toggle('collapsed');
                toggle.textContent = list.classList.contains('collapsed') ? '▶' : '▼';
            });
        });

        // Search functionality
        const searchInput = document.getElementById('pub-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.filterPublications();
            });
        }

        // Filter buttons (if needed for type filtering)
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentFilter = e.target.dataset.filter;
                this.filterPublications();
            });
        });

        // Expand/Collapse all button
        const expandAllBtn = document.getElementById('expand-all');
        const collapseAllBtn = document.getElementById('collapse-all');
        
        if (expandAllBtn) {
            expandAllBtn.addEventListener('click', () => this.toggleAllTopics(false));
        }
        if (collapseAllBtn) {
            collapseAllBtn.addEventListener('click', () => this.toggleAllTopics(true));
        }
    }

    /**
     * Toggle all topic sections and subtopics
     */
    toggleAllTopics(collapse) {
        // Toggle topics
        document.querySelectorAll('.topic-content').forEach(content => {
            if (collapse) {
                content.classList.add('collapsed');
            } else {
                content.classList.remove('collapsed');
            }
        });
        
        document.querySelectorAll('.topic-toggle').forEach(toggle => {
            toggle.textContent = collapse ? '▶' : '▼';
        });

        // Toggle subtopics
        document.querySelectorAll('.publications-list').forEach(list => {
            if (collapse) {
                list.classList.add('collapsed');
            } else {
                list.classList.remove('collapsed');
            }
        });
        
        document.querySelectorAll('.subtopic-toggle').forEach(toggle => {
            toggle.textContent = collapse ? '▶' : '▼';
        });
    }

    /**
     * Filter publications based on search term and filter type
     */
    filterPublications() {
        const items = document.querySelectorAll('.publication-item');
        let visibleCount = 0;

        items.forEach(item => {
            const title = item.querySelector('.pub-title').textContent.toLowerCase();
            const authors = item.querySelector('.pub-authors').textContent.toLowerCase();
            const venue = item.querySelector('.pub-venue').textContent.toLowerCase();
            const type = item.dataset.type;

            const matchesSearch = !this.searchTerm || 
                title.includes(this.searchTerm) || 
                authors.includes(this.searchTerm) || 
                venue.includes(this.searchTerm);

            const matchesFilter = this.currentFilter === 'all' || type === this.currentFilter;

            if (matchesSearch && matchesFilter) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        // Update topic visibility based on whether they have visible papers
        document.querySelectorAll('.topic-section').forEach(section => {
            const visiblePapers = section.querySelectorAll('.publication-item:not([style*="display: none"])');
            if (visiblePapers.length === 0) {
                section.style.display = 'none';
            } else {
                section.style.display = '';
            }
        });

        // Update search results count
        this.updateSearchResults(visibleCount);
    }

    /**
     * Update search results count
     */
    updateSearchResults(count) {
        let resultsDiv = document.getElementById('search-results');
        if (!resultsDiv) {
            resultsDiv = document.createElement('div');
            resultsDiv.id = 'search-results';
            resultsDiv.style.cssText = 'text-align: center; margin: 1rem 0; color: var(--text-secondary);';
            const container = document.getElementById('publications-container');
            if (container) {
                container.parentNode.insertBefore(resultsDiv, container);
            }
        }

        if (this.searchTerm) {
            resultsDiv.textContent = `Found ${count} publication${count !== 1 ? 's' : ''} matching "${this.searchTerm}"`;
            resultsDiv.style.display = 'block';
        } else {
            resultsDiv.style.display = 'none';
        }
    }

    /**
     * Update publication statistics
     */
    updateStats() {
        const totalPapers = this.data.topics.reduce((sum, topic) => 
            sum + topic.subtopics.reduce((subSum, subtopic) => 
                subSum + subtopic.papers.length, 0), 0);

        const statsElement = document.querySelector('.footer-section p[style*="font-size: 2rem"]');
        if (statsElement) {
            statsElement.textContent = `${Math.floor(totalPapers / 100) * 100}+`;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const pubManager = new PublicationsManager();
    pubManager.init().catch(error => {
        console.error('Failed to initialize publications:', error);
        // Show error message to user
        const container = document.getElementById('publications-container');
        if (container) {
            const errorDetails = error.message || 'Unknown error';
            const isCORS = errorDetails.includes('fetch') || errorDetails.includes('CORS');
            
            container.innerHTML = `
                <div class="card" style="border-left: 4px solid #e74c3c;">
                    <h3 style="color: #e74c3c;">⚠️ Error Loading Publications</h3>
                    <p><strong>Error:</strong> ${errorDetails}</p>
                    ${isCORS ? `
                        <div style="background: #fff3cd; padding: 1rem; border-radius: 4px; margin-top: 1rem;">
                            <p style="margin: 0;"><strong>💡 Tip:</strong> This page needs to be served through a web server (not opened directly as a file).</p>
                            <p style="margin: 0.5rem 0 0 0;">Try running: <code style="background: #f5f5f5; padding: 0.2rem 0.5rem; border-radius: 3px;">python3 -m http.server 8000</code></p>
                            <p style="margin: 0.5rem 0 0 0;">Then open: <code style="background: #f5f5f5; padding: 0.2rem 0.5rem; border-radius: 3px;">http://localhost:8000/publications.html</code></p>
                        </div>
                    ` : ''}
                    <p style="margin-top: 1rem;">Check the browser console (F12) for more details.</p>
                </div>
            `;
        }
    });
});
