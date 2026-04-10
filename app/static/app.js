/**
 * Web Text Board - Editor JavaScript
 * Mobile-first plain text editor with manual save
 */

(function() {
    'use strict';

    const MIN_FONT_SIZE = 12;
    const MAX_FONT_SIZE = 40;

    let editor;
    let currentFontSize;

    function initEditor(savedFontSize) {
        editor = document.getElementById('editor');
        currentFontSize = savedFontSize || 18;

        setFontSize(currentFontSize);

        document.getElementById('btn-clear').addEventListener('click', handleClear);
        document.getElementById('btn-a-minus').addEventListener('click', handleFontMinus);
        document.getElementById('btn-a-plus').addEventListener('click', handleFontPlus);
        document.getElementById('btn-save').addEventListener('click', handleSave);

        setupPinchToZoom();

        editor.focus();
    }

    function setFontSize(size) {
        currentFontSize = Math.max(MIN_FONT_SIZE, Math.min(MAX_FONT_SIZE, size));
        editor.style.fontSize = currentFontSize + 'px';
    }

    function handleClear() {
        if (confirm('Clear all text? This cannot be undone.')) {
            editor.value = '';
            saveToServer(editor.value, currentFontSize);
        }
    }

    function handleFontMinus() {
        setFontSize(currentFontSize - 1);
    }

    function handleFontPlus() {
        setFontSize(currentFontSize + 1);
    }

    function handleSave() {
        saveToServer(editor.value, currentFontSize);
    }

    async function saveToServer(content, fontSize) {
        try {
            await fetch('/api/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    font_size_px: fontSize
                })
            });
        } catch (err) {
            console.error('Save failed:', err);
        }
    }

    function setupPinchToZoom() {
        let initialDistance = 0;
        let initialFontSize = currentFontSize;

        editor.addEventListener('touchstart', function(e) {
            if (e.touches.length === 2) {
                initialDistance = getDistance(e.touches[0], e.touches[1]);
                initialFontSize = currentFontSize;
            }
        }, { passive: true });

        editor.addEventListener('touchmove', function(e) {
            if (e.touches.length === 2) {
                if (!initialDistance) return;
                const currentDistance = getDistance(e.touches[0], e.touches[1]);
                const scale = currentDistance / initialDistance;
                const newSize = Math.round(initialFontSize * scale);
                setFontSize(newSize);
            }
        }, { passive: true });
    }

    function getDistance(touch1, touch2) {
        const dx = touch2.clientX - touch1.clientX;
        const dy = touch2.clientY - touch1.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    window.initEditor = initEditor;
})();
