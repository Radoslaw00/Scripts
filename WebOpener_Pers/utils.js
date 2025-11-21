/**
 * Utilities Module - JavaScript
 * Shared utility functions across the application
 */

export const utils = {
    /**
     * Render a list of items as links
     */
    renderItems(container, items, linkClass) {
        container.innerHTML = '';
        items.forEach(item => {
            const link = document.createElement('a');
            link.href = item.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.className = linkClass;
            link.innerHTML = `
                <div class="${linkClass.replace('-link', '-icon')}">${item.emoji}</div>
                <div class="${linkClass.replace('-link', '-name')}">${item.name}</div>
            `;
            container.appendChild(link);
        });
    },

    /**
     * Sites data
     */
    sitesData: [
        { name: 'YouTube', url: 'https://youtube.com', emoji: '▶️' },
        { name: 'GitHub', url: 'https://github.com', emoji: '🐙' },
        { name: 'Facebook', url: 'https://facebook.com', emoji: '👥' },
        { name: 'Gmail', url: 'https://mail.google.com', emoji: '📧' },
        { name: 'Google', url: 'https://google.com', emoji: '🔍' },
        { name: 'ChatGPT', url: 'https://chatgpt.com', emoji: '🤖' },
        { name: 'X', url: 'https://x.com', emoji: '❌' },
        { name: 'TikTok', url: 'https://tiktok.com', emoji: '📱' },
        { name: 'Allegro', url: 'https://allegro.pl', emoji: '🛍️' },
        { name: 'OLX', url: 'https://olx.pl', emoji: '💼' },
        { name: 'Apple', url: 'https://apple.com', emoji: '🍎' },
        { name: 'Rumble', url: 'https://rumble.com', emoji: '🔴' }
    ],

    /**
     * Games data
     */
    gamesData: [
        { name: 'Diep.io', url: 'https://diep.io', emoji: '⚫' },
        { name: 'Slither.io', url: 'https://slither.io', emoji: '🐍' },
        { name: 'Agar.io', url: 'https://agar.io', emoji: '🟢' },
        { name: 'Mope.io', url: 'https://mope.io', emoji: '🦁' },
        { name: 'Arras.io', url: 'https://arras.io', emoji: '🎯' },
        { name: 'Chess.com', url: 'https://chess.com', emoji: '♟️' }
    ]
};

// Prevent link opening on certain conditions
document.addEventListener('auxclick', (e) => {
    if (e.button === 1) {
        // Middle click - handled by browser
    }
});
