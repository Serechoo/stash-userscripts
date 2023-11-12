// ==UserScript==
// @name         Batch Create All 0.3
// @namespace    http://tampermonkey.net/
// @version      0.3.1
// @description  Adds a 'Create All' button much like the 'Search All' button that interacts with all create buttons. The idea is to run the 'Search All' button first, and then run this one.
// @author       Serechoo
// @match        http://localhost:9999/scenes?*disp=3*
// @grant        unsafeWindow
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// @connect      localhost
// ==/UserScript==

(function () {
    'use strict';

    console.log("Script started"); // Debugging statement

    // Add the following styles
    GM_addStyle(`
        .modal-container {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #fff;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            z-index: 9999;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
        }

        .modal-content {
            text-align: center;
            font-size: 16px;
            color: #333;
        }

        .progress-bar-container {
            position: relative;
            height: 20px;
        }

        .progress-bar {
            width: 0;
            height: 100%;
            background-color: #4CAF50;
            transition: width 0.3s;
            border-radius: 5px;
        }

        .percentage-counter {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #fff;
        }
    `);

    // Rest of your script code...

})();

(function () {
    'use strict';

    const DEFAULT_DELAY = 500; // Set your desired delay in milliseconds
    let delay = DEFAULT_DELAY;

    const {
        stash,
        waitForElementByXpath,
        getElementByXpath,
        sortElementChildren,
    } = unsafeWindow.stash;

    let running = false;
    let maxCreateCount = 0;
    let maxTagCount = 0;

    // Custom modal elements
    const modalContainer = document.createElement("div");
    modalContainer.classList.add("modal-container");
    modalContainer.style.display = "none";

    const modalContent = document.createElement("div");
    modalContent.classList.add("modal-content");
    modalContainer.appendChild(modalContent);

    const progressBarContainer = document.createElement("div");
    progressBarContainer.classList.add("progress-bar-container");
    modalContainer.appendChild(progressBarContainer);

    const progressBar = document.createElement("div");
    progressBar.classList.add("progress-bar");
    progressBarContainer.appendChild(progressBar);

    const percentageCounter = document.createElement("div");
    percentageCounter.classList.add("percentage-counter");
    progressBarContainer.appendChild(percentageCounter);

    document.body.appendChild(modalContainer);

    async function run() {
        if (!running) return;

        const createButtons = document.querySelectorAll('.search-result .btn-group');
        const tagButtons = document.querySelectorAll('button.minimal.ml-2.btn.btn-primary');
        maxCreateCount = createButtons.length;
        maxTagCount = tagButtons.length;
        stash.setProgress((maxCreateCount - createButtons.length) / maxCreateCount * 100);

        let completedCreateCount = 0;
        let completedTagCount = 0;
        let totalElapsedTimeCreate = 0;
        let totalElapsedTimeTag = 0;

        // Process 'Create' buttons
        for (const createButtonGroup of createButtons) {
            const selectPlaceholder = createButtonGroup.querySelector('.react-select__placeholder');
            const buttons = createButtonGroup.querySelectorAll('button.btn.btn-secondary');
            const startTime = performance.now();

            for (const button of buttons) {
                const selectText = selectPlaceholder?.textContent?.trim();
                const buttonText = button?.textContent?.trim();
                if (!['Select Performer', 'Select Studio'].includes(selectText)) continue;
                if (button.disabled || buttonText !== 'Create') continue;
                button.click();
                await delayAction(delay); // Wait for 500ms

                // Add your interaction logic here for the 'Create' button, if needed.
                // For example, fill out a form or perform actions.

                // Click the 'Save' button in the modal footer of the new window
                const saveButton = document.querySelector('.ModalFooter.modal-footer button.btn.btn-primary');
                if (saveButton) {
                    saveButton.click();
                    await delayAction(delay); // Wait for 500ms
                    // Add your interaction logic here for the 'Save' button in the new window.
                }

                const elapsedTime = performance.now() - startTime;
                totalElapsedTimeCreate += elapsedTime;

                completedCreateCount++;

                const progressCreate = completedCreateCount / maxCreateCount * 100;
                stash.setProgress(progressCreate);

                // Update modal content for 'Create'
                const remainingTimeCreate = calculateRemainingTime(completedCreateCount, maxCreateCount, totalElapsedTimeCreate);
                const etaCreate = formatTime(remainingTimeCreate);
                updateModalContent(progressCreate, etaCreate);
            }
        }

        // Process tags independently
        for (const tagbutton of tagButtons) {
            tagbutton.click();
            await delayAction(1000); // Wait for 1000ms
            // Add your interaction logic here for the tags, if needed.

            completedTagCount++;

            const progressTag = completedTagCount / maxTagCount * 100;
            stash.setProgress(progressTag);

            // Update modal content for 'Tags'
            const remainingTimeTag = calculateRemainingTime(completedTagCount, maxTagCount, totalElapsedTimeTag);
            const etaTag = formatTime(remainingTimeTag);
            updateModalContent(progressTag, etaTag);
        }

        stop();
    }

    function calculateRemainingTime(completedCount, maxCount, totalElapsedTime) {
        const remainingCount = maxCount - completedCount;
        const averageTimePerTask = totalElapsedTime / completedCount;
        return remainingCount * averageTimePerTask;
    }

    function formatTime(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        const formattedSeconds = seconds % 60;
        const formattedMinutes = minutes % 60;
        const formattedHours = hours;

        return `ETA ${formattedHours}h ${formattedMinutes}m ${formattedSeconds}s`;
    }

    function updateModalContent(progress, eta) {
        progressBar.style.width = `${progress}%`;
        percentageCounter.textContent = `${progress.toFixed(2)}%`;
        modalContent.textContent = `Progress: ${progress.toFixed(2)}% - ${eta}`;
    }

    const btnId = 'batch-create'; // Change the button ID to 'batch-create'
    const startLabel = 'Create All'; // Change the button label to 'Create All'
    const stopLabel = 'Stop Create All';
    const btn = document.createElement("button");
    btn.setAttribute("id", btnId);
    btn.classList.add('btn', 'btn-primary', 'ml-3');
    btn.innerHTML = startLabel;
    btn.onclick = () => {
        if (running) stop();
        else start();
    };

    function start() {
        btn.innerHTML = stopLabel;
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-danger');
        running = true;
        stash.setProgress(0);
        modalContainer.style.display = "block"; // Show the modal when starting
        run();
    }

    function stop() {
        btn.innerHTML = startLabel;
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-primary');
        running = false;
        stash.setProgress(0);
        modalContainer.style.display = "none"; // Hide the modal when stopping
    }

    stash.addEventListener('page:performers', function () {
        waitForElementByXpath("//button[text()='Batch Update Performers']", function (xpath, el) {
            if (!document.getElementById(btnId)) {
                const container = el.parentElement;
                container.appendChild(btn);
            }
        });
    });

    stash.addEventListener('tagger:mutations:header', () => {
        const el = getElementByXpath("//button[text()='Scrape All']");
        if (el && !document.getElementById(btnId)) {
            const container = el.parentElement;
            container.appendChild(btn);
            sortElementChildren(container);
            el.classList.add('ml-3');
        }
    });

    const batchSearchConfigId = 'batch-create-config'; // Change the config ID

    async function loadSettings() {
        delay = parseInt(await GM_getValue('batch-create-delay', DEFAULT_DELAY));
        const input = document.querySelector(`#${batchSearchConfigId} input[type="text"]`);
        input.value = delay;
        input.addEventListener('change', async () => {
            let value = parseInt(input.value.trim())
            value = isNaN(value) ? DEFAULT_DELAY : value;
            input.value = value;
            delay = value;
            await GM_setValue('batch-create-delay', value);
        });
    }

    // Function to delay actions
    const delayAction = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    loadSettings();
})();
