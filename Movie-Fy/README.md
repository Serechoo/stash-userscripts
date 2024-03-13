Movie-fy

The Movie-fy tool is designed to assist in managing and creating movies within Stash.

Instructions: 

Ensure to 'pip install thefuzz' as it is required for the fuzzy matching of your scene titles against the local 'Movie-Fy.json' reference.

Please copy the entire contents of the Movie-Fy folder into your plugins directory and then 'Reload Your Plugins'

The workflow is now fairly straightforward. 

1. Go to your 'Tasks' section, scroll down and start by selecting the 'Movie-Fy Create Movie Studio' task. This will automatically create the 'Movie' studio within your Stash. This only has to be run one time. The 'Movie' studio acts
   as a management container for your movie scenes so that the GraphQL queries and mutations have a way to target your specific movie scenes.

2. Load your movie scenes into your Stash. If they are already present, bulk update your scenes studio to be the 'Movie' studio. If you have new scenes that you are importing directly into Stash for the first time, you will need to run an additional step to
   ensure Movie-Fy can see your scenes. Since Movie-Fy looks for scene titles and matches those against the local 'Movie-Fy URLs.json' to be able to pull URLs for scraping and appending the proper metadata to your movies, you will need to
   go to the 'Tasks' section again, and select the 'Movie-Fy Check and Update Scene Titles' task. All this does is target any scenes within the 'Movie' studio and creates a title within Stash for them. Now, Movie-Fy should be able to see your scenes and start managing them.

3. This is when you'll launch the main Movie-Fy.py script. Open a terminal from within your plugins folder, or navigate to it accordingly via the terminal and type 'python Movie-Fy.py' and hit Enter. You should see the Movie-Fy script perform an initial GraphQL query to determine how many scenes you now have to work
   through. If you have your scenes named well and without clutter, this will give Movie-Fy the best chance for success to be able to automatically match these scene titles to different hits within the local JSON. Once a match is made, simply enter the corresponding number for the movie you would like to create
   based on the scene's match. Movie-Fy will scan your Stash to see if a movie by the same title already exists. If none exist, it will create the movie for you and append the associated URL (to be scraped later). If a match is found, it will confirm with you that you would like to add that scene to the existing movie.
   
  Since a URL is provided for any matches, you can feel free to visit them to confirm it is the right movie you're adding and updating before making the final decision to proceed.

4. Once you have gone through this loop, you should have a bunch of blank movie containers created with the proper scenes existing within each of them! Head on over to your Tasks section once more and click on the 'Movie-Fy Bulk Movie Scraper' task. This will bulk scrape all of those URLs you have just added to
   those movie containers and update your movies with the appropriate metadata including front_image, back_image, synopsis, and date.

5. Now, you can click on the 'Movie-Fy Update Movie Scene Covers' task to update all your scene preview images to match the cover of your newly scraped movie (this is completely optional, of course)

6. Finally, you will have to manually review the newly created movies and attach a proper Studio to them. Once you've done this you can head back to the Tasks section and select the 'Movie-Fy Scene Studio Bulk Update' task to automatically bulk update your scenes with the same Studio as your movie for uniformity (again, completely optional)

Please feel free to reach out in the Stash Discord for any questions. I may not be able to answer right away, but would be more than happy to help get you started!

My recommendation is to start with a few movies until you get the workflow down. Then, enjoy bulk updating your movie collection into Stash!

Enjoy!
