(function () {
    'use strict';

    console.log("Script started"); // Debugging statement

    const DEFAULT_DELAY = 100; // Set your desired delay in milliseconds
    let delay = DEFAULT_DELAY;
    let running = false;
    let maxCreateCount = 0;
    let maxTagCount = 0;

    async function run() {
        if (!running) return;

        const createButtons = document.querySelectorAll('.btn-group');
        const tagButtons = document.querySelectorAll('button.minimal.ml-2.btn.btn-primary');
        maxCreateCount = createButtons.length;
        maxTagCount = tagButtons.length;

        // Process 'Create' buttons
        for (const createButtonGroup of createButtons) {
            const selectPlaceholder = createButtonGroup.querySelector('.react-select__placeholder');
            const buttons = createButtonGroup.querySelectorAll('button.btn.btn-secondary');

            for (const button of buttons) {
                if (selectPlaceholder && (selectPlaceholder.textContent.trim() === 'Select Performer' || selectPlaceholder.textContent.trim() === 'Select Studio')) {
                    if (!button.disabled && button.textContent.trim() === 'Create') {
                        button.click();
                        await delayAction(delay); // Wait for the specified delay

                        // Add your interaction logic here for the 'Create' button, if needed.
                        // For example, fill out a form or perform actions.

                        // Click the 'Save' button in the modal footer of the new window
                        const saveButton = document.querySelector('.ModalFooter.modal-footer button.btn.btn-primary');
                        if (saveButton) {
                            saveButton.click();
                            await delayAction(delay); // Wait for the specified delay
                            // Add your interaction logic here for the 'Save' button in the new window.
                        }
                    }
                }
            }
        }

        // Process tags independently
        for (const tagbutton of tagButtons) {
            tagbutton.click();
            await delayAction(delay); // Wait for the specified delay
            // Add your interaction logic here for the tags, if needed.
        }

        stop();
    }

    // Function to delay actions
    async function delayAction(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
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

    // Function to place the button using custom event logic
    function placeButtonWithCustomEvent() {
        const el = getElementByXpath("//button[text()='Scrape All']");
        if (el && !document.getElementById(btnId)) {
            const container = el.parentElement;
            container.appendChild(btn);
            sortElementChildren(container);
            el.classList.add('ml-3');
        }
    }

    // Wait for the specified delay (e.g., 2 seconds) before placing the button using custom event logic
    setTimeout(placeButtonWithCustomEvent, 2000); // Adjust the delay as needed

    // Custom event listener for button placement
    document.addEventListener('customButtonPlacementEvent', function (evt) {
        placeButtonWithCustomEvent();
    });

    function start() {
        btn.innerHTML = stopLabel;
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-danger');
        running = true;
        run();
    }

    function stop() {
        btn.innerHTML = startLabel;
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-primary');
        running = false;
    }

    loadSettings(); // Initialize settings

    // Function to load settings if needed
    async function loadSettings() {
        // Implement your logic to load settings here if required.
        // Example: delay = parseInt(await getSetting('delay', DEFAULT_DELAY));
    }

    // Implement a function to save settings if needed.
    // async function saveSettings() {
    //     // Example: await setSetting('delay', delay);
    // }
})();