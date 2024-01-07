// ==UserScript==
// @name         Pornhub Viewkey Downloader
// @namespace    https://www.github.com/Serechoo/stash-userscripts
// @version      1.0
// @description  Add visual cues to video links with viewkey and collect them for download with yt-dl
// @author       Serechoo
// @match        https://www.pornhub.com/*
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    const selectedLinks = new Map(); // Using Map to store link statuses

    // Function to copy text to clipboard
    const copyToClipboard = (text) => {
        if (typeof GM_setClipboard !== 'undefined') {
            GM_setClipboard(text); // If using Tampermonkey with GM_setClipboard available
        } else {
            // Clipboard access might not be available in all userscript contexts
            // You might need to manually copy the text or use other methods here
            console.log('Clipboard access not available in this context. Text:', text);
        }
    };

    const toggleSelection = (icon, link) => {
        if (!selectedLinks.has(link.href)) {
            icon.innerHTML = '🔗'; // Change icon to a chain link when clicked
            selectedLinks.set(link.href, false); // Add the link to the list of selected links with initial state
        } else if (!selectedLinks.get(link.href)) {
            icon.innerHTML = '📋'; // Change icon to a clipboard if clicked again to indicate copied
            selectedLinks.set(link.href, true); // Change state to indicate link is copied
            copyToClipboard(link.href); // Copy the link to the clipboard
        }
    };

    const videoLinks = document.querySelectorAll('a[href*="viewkey"]');

    videoLinks.forEach(link => {
        if (link.classList.contains('fade') && link.classList.contains('videoPreviewBg') && link.classList.contains('linkVideoThumb') && link.classList.contains('js-linkVideoThumb') && link.classList.contains('img') && link.classList.contains('fadeUp')) {
            return; // Skip icons for video preview cards
        }

        const icon = document.createElement('span');
        icon.innerHTML = '🔑';
        link.insertBefore(icon, link.firstChild);

        icon.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default navigation behavior
            toggleSelection(icon, link);
        }, { passive: false });
    });

    const clipboardButton = document.createElement('button');
    clipboardButton.textContent = 'Copy to Clipboard';
    clipboardButton.style.backgroundColor = 'rgba(76, 175, 80, 0.6)'; // Transparent green background color
    clipboardButton.style.color = 'white';
    clipboardButton.style.border = 'none';
    clipboardButton.style.padding = '10px 20px';
    clipboardButton.style.textAlign = 'center';
    clipboardButton.style.textDecoration = 'none';
    clipboardButton.style.display = 'inline-block';
    clipboardButton.style.fontSize = '16px';
    clipboardButton.style.marginRight = '10px';
    clipboardButton.style.cursor = 'pointer';
    clipboardButton.style.borderRadius = '5px'; // Rounded corners

    clipboardButton.addEventListener('click', () => {
        // Copy all selected URLs to the clipboard
        const copiedLinks = [];
        Array.from(selectedLinks.keys()).forEach(key => {
            if (!selectedLinks.get(key)) {
                selectedLinks.set(key, true); // Change state to indicate link is copied
                copyToClipboard(key);
                copiedLinks.push(key);
            }
        });

        if (copiedLinks.length > 0) {
            const icons = document.querySelectorAll('a[href*="viewkey"] span');
            icons.forEach(icon => {
                const link = icon.parentElement;
                if (copiedLinks.includes(link.href)) {
                    icon.innerHTML = '📋'; // Change icons to clipboard to indicate copied
                }
            });
            alert('Selected URLs copied to clipboard!');
        } else {
            alert('All selected URLs are already copied to clipboard!');
        }
    }, { passive: true });

    const downloadButton = document.createElement('button');
    downloadButton.textContent = 'Download URLs as urls.txt';
    downloadButton.style.backgroundColor = 'rgba(0, 140, 186, 0.6)'; // Transparent blue background color
    downloadButton.style.color = 'white';
    downloadButton.style.border = 'none';
    downloadButton.style.padding = '10px 20px';
    downloadButton.style.textAlign = 'center';
    downloadButton.style.textDecoration = 'none';
    downloadButton.style.display = 'inline-block';
    downloadButton.style.fontSize = '16px';
    downloadButton.style.cursor = 'pointer';
    downloadButton.style.borderRadius = '5px'; // Rounded corners

    downloadButton.addEventListener('click', () => {
        // Create a text file with selected URLs and initiate download
        const urlsText = Array.from(selectedLinks.keys()).join('\n');
        const downloadLink = document.createElement('a');
        downloadLink.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(urlsText);
        downloadLink.download = 'urls.txt';
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }, { passive: true });

    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '20px'; // Adjust top positioning as needed
    container.style.right = '20px'; // Adjust right positioning as needed
    container.style.zIndex = '9999'; // Ensure it stays above other elements
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '10px'; // Adjust gap between buttons as needed
    container.appendChild(clipboardButton);
    container.appendChild(downloadButton);
    document.body.appendChild(container);
})();
