/**
 * File Drop Analyzer
 * Analyzes dropped files and displays statistics
 */

class FileAnalyzer {
    constructor() {
        this.files = [];
        this.fileStats = {
            byType: {},
            byName: [],
            totalCount: 0
        };
        this.init();
    }

    init() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const resetButton = document.getElementById('resetButton');

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults.bind(this), false);
            document.body.addEventListener(eventName, this.preventDefaults.bind(this), false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.handleDragEnter.bind(this), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.handleDragLeave.bind(this), false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', this.handleDrop.bind(this), false);

        // Handle click to select files
        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Reset button
        resetButton.addEventListener('click', this.reset.bind(this));

        this.updateUI();
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDragEnter(e) {
        document.getElementById('dropZone').classList.add('drag-over');
    }

    handleDragLeave(e) {
        if (e.target === document.getElementById('dropZone')) {
            document.getElementById('dropZone').classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        document.getElementById('dropZone').classList.remove('drag-over');
        const dt = e.dataTransfer;
        const items = dt.items;

        if (items) {
            // Use DataTransferItemList interface
            for (let i = 0; i < items.length; i++) {
                if (items[i].kind === 'file') {
                    const file = items[i].getAsFile();
                    this.files.push(file);
                }
            }
        } else {
            // Use DataTransfer interface (fallback)
            for (let i = 0; i < dt.files.length; i++) {
                this.files.push(dt.files[i]);
            }
        }

        this.analyzeFiles();
        this.updateUI();
    }

    handleFileSelect(e) {
        const files = e.target.files;
        for (let i = 0; i < files.length; i++) {
            this.files.push(files[i]);
        }
        this.analyzeFiles();
        this.updateUI();
    }

    analyzeFiles() {
        this.fileStats = {
            byType: {},
            byName: [],
            totalCount: 0
        };

        this.files.forEach(file => {
            // Get file extension
            const extension = file.name.split('.').pop().toLowerCase() || 'no-extension';
            const type = this.getFileType(extension);

            // Add to type stats
            if (!this.fileStats.byType[type]) {
                this.fileStats.byType[type] = {
                    extension: extension,
                    count: 0,
                    icon: this.getFileIcon(extension)
                };
            }
            this.fileStats.byType[type].count++;

            // Add to name list
            this.fileStats.byName.push({
                name: file.name,
                extension: extension,
                icon: this.getFileIcon(extension)
            });

            this.fileStats.totalCount++;
        });

        // Sort by name
        this.fileStats.byName.sort((a, b) => a.name.localeCompare(b.name));
    }

    getFileType(extension) {
        const typeMap = {
            // Images
            'jpg': 'images',
            'jpeg': 'images',
            'png': 'images',
            'gif': 'images',
            'svg': 'images',
            'webp': 'images',
            'bmp': 'images',
            'ico': 'images',

            // Documents
            'pdf': 'documents',
            'doc': 'documents',
            'docx': 'documents',
            'txt': 'documents',
            'rtf': 'documents',
            'odt': 'documents',

            // Spreadsheets
            'xls': 'spreadsheets',
            'xlsx': 'spreadsheets',
            'csv': 'spreadsheets',
            'ods': 'spreadsheets',

            // Presentations
            'ppt': 'presentations',
            'pptx': 'presentations',
            'odp': 'presentations',

            // Archives
            'zip': 'archives',
            'rar': 'archives',
            '7z': 'archives',
            'tar': 'archives',
            'gz': 'archives',

            // Audio
            'mp3': 'audio',
            'wav': 'audio',
            'flac': 'audio',
            'aac': 'audio',
            'ogg': 'audio',
            'm4a': 'audio',

            // Video
            'mp4': 'video',
            'avi': 'video',
            'mov': 'video',
            'mkv': 'video',
            'flv': 'video',
            'wmv': 'video',
            'webm': 'video',

            // Code
            'js': 'code',
            'ts': 'code',
            'py': 'code',
            'java': 'code',
            'cpp': 'code',
            'c': 'code',
            'php': 'code',
            'html': 'code',
            'css': 'code',
            'json': 'code',
            'xml': 'code',
            'yml': 'code',
            'yaml': 'code',

            // Data
            'json': 'data',
            'sql': 'data',
            'db': 'data',

            // Executables
            'exe': 'executables',
            'msi': 'executables',
            'bat': 'executables',
            'sh': 'executables',
            'app': 'executables'
        };

        return typeMap[extension] || 'other';
    }

    getFileIcon(extension) {
        const iconMap = {
            // Images
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🎬',
            'svg': '✨',
            'webp': '🖼️',
            'bmp': '🖼️',
            'ico': '📌',

            // Documents
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'txt': '📋',
            'rtf': '📝',
            'odt': '📝',

            // Spreadsheets
            'xls': '📊',
            'xlsx': '📊',
            'csv': '📊',
            'ods': '📊',

            // Presentations
            'ppt': '🎯',
            'pptx': '🎯',
            'odp': '🎯',

            // Archives
            'zip': '📦',
            'rar': '📦',
            '7z': '📦',
            'tar': '📦',
            'gz': '📦',

            // Audio
            'mp3': '🎵',
            'wav': '🎵',
            'flac': '🎵',
            'aac': '🎵',
            'ogg': '🎵',
            'm4a': '🎵',

            // Video
            'mp4': '🎥',
            'avi': '🎥',
            'mov': '🎥',
            'mkv': '🎥',
            'flv': '🎥',
            'wmv': '🎥',
            'webm': '🎥',

            // Code
            'js': '💻',
            'ts': '💻',
            'py': '🐍',
            'java': '☕',
            'cpp': '⚙️',
            'c': '⚙️',
            'php': '🔗',
            'html': '🌐',
            'css': '🎨',
            'json': '📋',
            'xml': '📋',
            'yml': '📋',
            'yaml': '📋',

            // Executables
            'exe': '⚡',
            'msi': '⚡',
            'bat': '⚡',
            'sh': '⚡',
            'app': '⚡'
        };

        return iconMap[extension] || '📄';
    }

    updateUI() {
        const dropZone = document.getElementById('dropZone');
        const resultsContainer = document.getElementById('resultsContainer');
        const emptyState = document.getElementById('emptyState');

        if (this.files.length === 0) {
            dropZone.style.display = 'block';
            resultsContainer.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            dropZone.style.display = 'none';
            emptyState.style.display = 'none';
            resultsContainer.style.display = 'block';
            this.renderResults();
        }
    }

    renderResults() {
        this.updateStats();
        this.renderFileTypes();
        this.renderFileList();
    }

    updateStats() {
        document.getElementById('totalFiles').textContent = this.fileStats.totalCount;
        document.getElementById('fileTypes').textContent = Object.keys(this.fileStats.byType).length;
    }

    renderFileTypes() {
        const container = document.getElementById('fileTypesGrid');
        container.innerHTML = '';

        Object.entries(this.fileStats.byType).forEach(([type, data]) => {
            const card = document.createElement('div');
            card.className = 'file-type-item';
            card.innerHTML = `
                <div class="file-type-icon">${data.icon}</div>
                <div class="file-type-name">${type}</div>
                <div class="file-type-count">${data.count}</div>
            `;
            container.appendChild(card);
        });
    }

    renderFileList() {
        const container = document.getElementById('filesList');
        container.innerHTML = '';

        this.fileStats.byName.forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <span class="file-item-icon">${file.icon}</span>
                <span class="file-item-name">${file.name}</span>
            `;
            container.appendChild(item);
        });
    }

    reset() {
        this.files = [];
        this.fileStats = {
            byType: {},
            byName: [],
            totalCount: 0
        };
        document.getElementById('fileInput').value = '';
        this.updateUI();
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    new FileAnalyzer();
});
