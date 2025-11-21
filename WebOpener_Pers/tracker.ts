/**
 * Analytics Tracker - TypeScript
 * Tracks how many times sites and games pages are opened
 * Data persisted in localStorage
 */

interface PageStats {
    sitesOpened: number;
    gamesOpened: number;
    lastUpdated: string;
}

class AnalyticsTracker {
    private readonly STORAGE_KEY = 'web_opener_stats';
    private stats: PageStats;

    constructor() {
        this.stats = this.loadStats();
    }

    /**
     * Load stats from localStorage or create new ones
     */
    private loadStats(): PageStats {
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

    /**
     * Save stats to localStorage
     */
    private saveStats(): void {
        this.stats.lastUpdated = new Date().toISOString();
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.stats));
    }

    /**
     * Increment sites counter
     */
    public incrementSites(): void {
        this.stats.sitesOpened++;
        this.saveStats();
        this.updateDisplay();
    }

    /**
     * Increment games counter
     */
    public incrementGames(): void {
        this.stats.gamesOpened++;
        this.saveStats();
        this.updateDisplay();
    }

    /**
     * Get current stats
     */
    public getStats(): PageStats {
        return { ...this.stats };
    }

    /**
     * Update the display of stats in the UI
     */
    public updateDisplay(): void {
        const tracker = document.getElementById('statsTracker');
        if (tracker) {
            tracker.textContent = `Games opened: ${this.stats.gamesOpened} times | Sites opened: ${this.stats.sitesOpened} times`;
        }
    }

    /**
     * Reset all stats
     */
    public resetStats(): void {
        this.stats = {
            sitesOpened: 0,
            gamesOpened: 0,
            lastUpdated: new Date().toISOString()
        };
        this.saveStats();
        this.updateDisplay();
    }
}

// Export for use in other modules
export const tracker = new AnalyticsTracker();
