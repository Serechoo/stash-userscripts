# Batch Create All - Stash
This is a code to allow batch create jobs for your stash. 

The idea behind it is this: Once you have the userscripts for 'Batch Search' installed, you can then look to click the 'Create All' button that is installed via this javascript. 

0.2 changes - Currently, it should be able to iterate through every 'Create' button on the page that is created after you perform your 'Search All' and click it. There is also a tad of logic built in with this update where it should detect the placeholder text
of the container of the 'Create' button, and only click it if the placeholder text is 'Select Performer' or 'Select Studio'...otheriwse, it will skip that Create button and move on to the next.
