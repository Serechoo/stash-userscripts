# Batch Create All - Stash 0.1
This is a code to allow batch create jobs for your stash. 

The idea behind it is this: Once you have the userscripts for 'Search All' installed and click it, you can then look to click the 'Create All' button that is installed via this javascript. 

**Known bug currently**: Please refresh the page when you get to the Tagger view in the 'Scenes' page. This should load the 'Create All' button.

**Please note:** This script has only been tested in Chrome and in conjunction with the Neon Dark theme. Since it does target specific elements within the theme, it may have to be modified/generalized to work with other themes.

**Another note:** This version of the script does not have logic in place (yet) to detect already added performers and studios that may exist in your Stash. As a result, Stash will throw plenty of errors during the automation, but otherwise, the script should complete successfully, albeit a bit messy.

Credit for the button template and other great scripts to:

https://github.com/7dJx1qP/stash-userscripts


# Batch Create All - Stash 0.2

Added logic to the script to attempt to handle performers and studios that have already been created. There was a prior iteration of this script, but it would stop abruptly on the first new 'Create' button if a performer or studio was not present. That should now be fixed.

This script will skip scenes which already have the performer and studios detected, and should only interact with 'Create' buttons which have the default placeholder texts of 'Select Studio' or 'Select Performer' and click the 'Create' and 'Save' buttons accordingly.

This will not click the 'Save All' button, and let the user review the added Performers and Studios before committing the change.

# Batch Create All - Stash 0.3

Included the functionality to batch add any outstanding tags on the page.

Implemented a basic progress tracker of the overall task that will show as a percentage completion bar and give an estimated time until completion.

# Batch Create All - Stash 0.4

This is now a Custom JS you can copy and paste into the 'Custom Javascript' option in your 'Interface' options. 

If the 'Create All' button does not show on first load, reload the page and it should appear and be functional.
