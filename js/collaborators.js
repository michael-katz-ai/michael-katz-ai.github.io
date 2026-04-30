/**
 * Collaborators Manager
 * Handles loading and displaying research collaborators
 */

class CollaboratorsManager {
    constructor() {
        this.collaborators = [];
    }

    /**
     * Load collaborators data from JSON file
     */
    async loadData() {
        try {
            const response = await fetch('data/collaborators.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.collaborators = await response.json();
            return this.collaborators;
        } catch (error) {
            console.error('Error loading collaborators data:', error);
            throw error;
        }
    }

    /**
     * Initialize the collaborators page
     */
    async init() {
        await this.loadData();
        this.updateStats();
        this.renderTopCollaborators();
        this.renderAllCollaborators();
        this.setupSearch();
    }

    /**
     * Update statistics
     */
    updateStats() {
        const totalElement = document.getElementById('total-collaborators');
        if (totalElement) {
            totalElement.textContent = `${this.collaborators.length}`;
        }
    }

    /**
     * Render top collaborators (5+ papers)
     */
    renderTopCollaborators() {
        const container = document.getElementById('top-collaborators');
        if (!container) return;

        const topCollaborators = this.collaborators.filter(c => c.papers >= 5);
        
        container.innerHTML = topCollaborators.map(collab => `
            <div class="card fade-in" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👤</div>
                <h3 style="color: var(--primary-blue); margin-bottom: 0.5rem; font-size: 1.125rem;">${this.cleanName(collab.name)}</h3>
                <p style="color: var(--gray-600); font-weight: 600;">${collab.papers} publication${collab.papers !== 1 ? 's' : ''}</p>
            </div>
        `).join('');
    }

    /**
     * Render all collaborators in columns
     */
    renderAllCollaborators() {
        const container = document.getElementById('all-collaborators');
        if (!container) return;

        container.innerHTML = this.collaborators.map(collab => `
            <div class="collaborator-item" style="margin-bottom: 0.75rem; break-inside: avoid;">
                <strong>${this.cleanName(collab.name)}</strong>
                <span style="color: var(--gray-600); margin-left: 0.5rem;">(${collab.papers})</span>
            </div>
        `).join('');
    }

    /**
     * Clean up name (remove suffixes like "0001")
     */
    cleanName(name) {
        return name.replace(/\s+\d{4}$/, '');
    }

    /**
     * Setup search functionality
     */
    setupSearch() {
        const searchInput = document.getElementById('collab-search');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            this.filterCollaborators(searchTerm);
        });
    }

    /**
     * Filter collaborators based on search term
     */
    filterCollaborators(searchTerm) {
        const items = document.querySelectorAll('.collaborator-item');
        let visibleCount = 0;

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        // Also filter top collaborators
        const topCards = document.querySelectorAll('#top-collaborators .card');
        topCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const collabManager = new CollaboratorsManager();
    collabManager.init().catch(error => {
        console.error('Failed to initialize collaborators:', error);
        const container = document.getElementById('all-collaborators');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--error-red);">
                    <h3>⚠️ Error Loading Collaborators</h3>
                    <p>Unable to load collaborators data. Please try refreshing the page.</p>
                </div>
            `;
        }
    });
});

// Made with Bob
