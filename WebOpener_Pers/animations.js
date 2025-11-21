/**
 * Animation Module - JavaScript
 * Handles all smooth animations and transitions
 */

export const animationModule = {
    /**
     * Add staggered animation to elements on page load
     */
    animateElementsOnLoad(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el, index) => {
            el.style.animationDelay = `${index * 0.05}s`;
            el.style.animation = 'slideUp 0.5s ease-out forwards';
            el.style.opacity = '0';
        });
    },

    /**
     * Add click feedback animation
     */
    addClickFeedback() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('.site-link, .game-link, .btn, .back-btn');
            if (link) {
                link.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    link.style.transform = '';
                }, 150);
            }
        });
    },

    /**
     * Add touch device support
     */
    setupTouchSupport() {
        if (this.isTouchDevice()) {
            const links = document.querySelectorAll('.site-link, .game-link, .btn');
            links.forEach(link => {
                link.addEventListener('touchstart', function () {
                    this.style.opacity = '0.8';
                });
                link.addEventListener('touchend', function () {
                    this.style.opacity = '1';
                });
            });
        }
    },

    /**
     * Check if device supports touch
     */
    isTouchDevice() {
        return (
            (typeof window !== 'undefined' &&
                ('ontouchstart' in window ||
                    (window.DocumentTouch && typeof document !== 'undefined' && document instanceof window.DocumentTouch))) ||
            false
        );
    },

    /**
     * Optimize scroll performance with RequestAnimationFrame
     */
    optimizeScrollPerformance() {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    // Scroll-based animations can go here
                    ticking = false;
                });
                ticking = true;
            }
        });
    },

    /**
     * Initialize all animations
     */
    init() {
        this.animateElementsOnLoad('.site-link, .game-link, .btn');
        this.addClickFeedback();
        this.setupTouchSupport();
        this.optimizeScrollPerformance();
        document.documentElement.style.scrollBehavior = 'smooth';
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        animationModule.init();
    });
} else {
    animationModule.init();
}
