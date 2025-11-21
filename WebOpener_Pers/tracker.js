// Analytics Tracker - JavaScript compiled version
// (This would be generated from tracker.ts in a real build setup)

class AnalyticsTracker {
    constructor() {
        this.STORAGE_KEY = 'web_opener_stats';
        this.stats = this.loadStats();
    }

    loadStats() {
        const stored = localStorage.getItem(this.STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
        return {
            sitesOpened: 0,
            gamesOpened: 0,
            lastUpdated: new Date().toISOString()
        };
    }

    saveStats() {
        this.stats.lastUpdated = new Date().toISOString();
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.stats));
    }

    incrementSites() {
        this.stats.sitesOpened++;
        this.saveStats();
        this.updateDisplay();
    }

    incrementGames() {
        this.stats.gamesOpened++;
        this.saveStats();
        this.updateDisplay();
    }

    getStats() {
        return { ...this.stats };
    }

    updateDisplay() {
        const tracker = document.getElementById('statsTracker');
        if (tracker) {
            tracker.textContent = `Games opened: ${this.stats.gamesOpened} times | Sites opened: ${this.stats.sitesOpened} times`;
        }
    }

    resetStats() {
        this.stats = {
            sitesOpened: 0,
            gamesOpened: 0,
            lastUpdated: new Date().toISOString()
        };
        this.saveStats();
        this.updateDisplay();
    }
}

// Global tracker instance
const tracker = new AnalyticsTracker();
