// ==UserScript==
// @name         Batch Create All 0.2
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  Adds a 'Create All' button much like the 'Search All' button that interacts with all create buttons. The idea is to run the 'Search All' button first, and then run this one.
// @author       Serechoo
// @match        http://localhost:9999/scenes?*disp=3*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=undefined.localhost
// @grant       unsafeWindow
// @grant       GM_setClipboard
// @grant       GM_getResourceText
// @grant       GM_addStyle
// @grant       GM.getValue
// @grant       GM.setValue
// @connect      localhost
// ==/UserScript==
(function () {
    'use strict';

    console.log("Script started"); // Debugging statement

    const DEFAULT_DELAY = 500; // Set your desired delay in milliseconds
    let delay = DEFAULT_DELAY;

    // Rest of your script code...

})();



(function () {
    'use strict';

    const DEFAULT_DELAY = 500; // Set your desired delay in milliseconds
    let delay = DEFAULT_DELAY;

    const {
        stash,
        Stash,
        waitForElementId,
        waitForElementClass,
        waitForElementByXpath,
        getElementByXpath,
        sortElementChildren,
        createElementFromHTML,
    } = unsafeWindow.stash;

    let running = false;
    let maxCount = 0;

    async function run() {
        if (!running) return;
        const createButtons = document.querySelectorAll('.btn-group');
        stash.setProgress((maxCount - createButtons.length) / maxCount * 100);
        for (const createButtonGroup of createButtons) {
            const selectPlaceholder = createButtonGroup.querySelector('.react-select__placeholder');
            const buttons = createButtonGroup.querySelectorAll('button.btn.btn-secondary');
            for (const button of buttons) {
                if (selectPlaceholder && (selectPlaceholder.textContent.trim() === 'Select Performer' || selectPlaceholder.textContent.trim() === 'Select Studio')) {
                    if (!button.disabled && button.textContent.trim() === 'Create') {
                        button.click();
                        await delayAction(500); // Wait for 500ms
                        // Add your interaction logic here for the 'Create' button, if needed.
                        // For example, fill out a form or perform actions.

                        // Click the 'Save' button in the modal footer of the new window
                        const saveButton = document.querySelector('.ModalFooter.modal-footer button.btn.btn-primary');
                        if (saveButton) {
                            saveButton.click();
                            await delayAction(500); // Wait for 500ms
                            // Add your interaction logic here for the 'Save' button in the new window.
                        }
                    }
                }
            }
        }
        stop();
    }

    const btnId = 'batch-create'; // Change the button ID to 'batch-create'
    const startLabel = 'Create All'; // Change the button label to 'Create All'
    const stopLabel = 'Stop Create All';
    const btn = document.createElement("button");
    btn.setAttribute("id", btnId);
    btn.classList.add('btn', 'btn-primary', 'ml-3');
    btn.innerHTML = startLabel;
    btn.onclick = () => {
        if (running) {
            stop();
        }
        else {
            start();
        }
    };

    function start() {
        btn.innerHTML = stopLabel;
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-danger');
        running = true;
        stash.setProgress(0);
        run();
    }

    function stop() {
        btn.innerHTML = startLabel;
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-primary');
        running = false;
        stash.setProgress(0);
    }

    stash.addEventListener('page:performers', function () {
        waitForElementByXpath("//button[text()='Batch Update Performers']", function (xpath, el) {
            if (!document.getElementById(btnId)) {
                const container = el.parentElement;
                container.appendChild(btn);
            }
        });
    });

    stash.addEventListener('tagger:mutations:header', evt => {
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
        delay = parseInt(await GM.getValue('batch-create-delay', DEFAULT_DELAY));
        const input = document.querySelector(`#${batchSearchConfigId} input[type="text"]`);
        input.value = delay;
        input.addEventListener('change', async () => {
            let value = parseInt(input.value.trim())
            if (isNaN(value)) {
                value = DEFAULT_DELAY;
            }
            input.value = value;
            delay = value;
            await GM.setValue('batch-create-delay', value);
        });
    }

    // Function to delay actions
    async function delayAction(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    loadSettings();
})();





