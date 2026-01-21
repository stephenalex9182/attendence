/**
 * Shared UI Utilities for vmedu
 */

const UI = {
    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - 'success', 'error', 'info'
     */
    showToast: (message, type = 'info') => {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;

        container.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    /**
     * Switch tabs in a dashboard
     * @param {string} tabId - The ID of the content section to show
     * @param {HTMLElement} linkElement - The nav link that was clicked
     */
    switchTab: (tabId, linkElement) => {
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(el => {
            el.classList.remove('active');
        });

        // Show selected content
        const target = document.getElementById(tabId);
        if (target) {
            target.classList.add('active');
        }

        // Update Nav Link styles
        if (linkElement) {
            document.querySelectorAll('.nav-link').forEach(el => {
                el.classList.remove('active');
            });
            linkElement.classList.add('active');
        }
    },

    /**
     * Confirm Action Dialog
     */
    confirm: async (message) => {
        return new Promise((resolve) => {
            if (window.confirm(message)) {
                resolve(true);
            } else {
                resolve(false);
            }
        });
    },

    /**
     * Mobile Sidebar Logic
     */
    toggleSidebar: () => {
        const sidebar = document.querySelector('.sidebar');
        let overlay = document.querySelector('.sidebar-overlay');

        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.onclick = UI.toggleSidebar;
            document.body.appendChild(overlay);
            // small delay for transition
            requestAnimationFrame(() => {
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
            });
        } else {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }
    }
};

// Add listener to auto-close sidebar on mobile when link is clicked
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const sidebar = document.querySelector('.sidebar');
            if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
                UI.toggleSidebar();
            }
        });
    });
});
