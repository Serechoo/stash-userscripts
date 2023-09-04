// ==UserScript==
// @name         Batch Create All
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
    const createButtons = [];
    let maxCount = 0;

    async function run() {
        if (!running) return;
        const createButton = createButtons.pop();
        stash.setProgress((maxCount - createButtons.length) / maxCount * 100);
        if (createButton) {
            // Check if either "Select Studio" or "Select Performer" exists in the same div.btn-group container
            const btnGroupContainer = createButton.closest('.btn-group');
            const selectStudio = btnGroupContainer.querySelector('.react-select__placeholder#react-select-2-placeholder');
            const selectPerformer = btnGroupContainer.querySelector('.react-select__placeholder#react-select-3-placeholder');

            if (selectStudio || selectPerformer) {
                if (!createButton.disabled) {
                    createButton.click();
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

            setTimeout(run, delay);
        }
        else {
            stop();
        }
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
        createButtons.length = 0;
        for (const button of document.querySelectorAll('.btn.btn-secondary')) {
            if (button.innerText.toLowerCase().includes('create')) {
                createButtons.push(button);
            }
        }
        maxCount = createButtons.length;
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

    stash.addEventListener('tagger:configuration', evt => {
        const el = evt.detail;
        if (!document.getElementById(batchSearchConfigId)) {
            const configContainer = el.parentElement;
            const batchSearchConfig = createElementFromHTML(`
<div id="${batchSearchConfigId}" class="col-md-6 mt-4">
<h5>Batch Create</h5> <!-- Change the title -->
<div class="row">
    <div class="align-items-center form-group col-md-12">
        <div class="row">
            <label title="" for="batch-create-delay" class="col-sm-2 col-form-label">Delay (ms)</label> <!-- Change the ID and label -->
            <div class="col-sm-10">
                <input type="text" id="batch-create-delay" class="query-text-field bg-secondary text-white border-secondary form-control" data-default="${DEFAULT_DELAY}" placeholder="${DEFAULT_DELAY}">
            </div>
        </div>
        <small class="form-text">Wait time in milliseconds between Create actions.</small> <!-- Change the description -->
    </div>
</div>
</div>
            `);
            configContainer.appendChild(batchSearchConfig);
            loadSettings();
        }
    });

    async function loadSettings() {
        for (const input of document.querySelectorAll(`#${batchSearchConfigId} input[type="text"]`)) {
            input.value = parseInt(await GM.getValue(input.id, input.dataset.default));
            delay = input.value;
            input.addEventListener('change', async () => {
                let value = parseInt(input.value.trim())
                if (isNaN(value)) {
                    value = parseInt(input.dataset.default);
                }
                input.value = value;
                delay = value;
                await GM.setValue(input.id, value);
            });
        }
    }

    // Function to delay actions
    async function delayAction(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
})();
