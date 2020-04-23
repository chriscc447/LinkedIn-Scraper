# LinkedIn-Scraper


## Dependencies:
* pandas
* numpy
* Selenium
* Chrome driver
* pickle
* networkx
* pyvis

## Running the code: scraper.py and vis.py

### scraper.py
This file contains the LI_Scraper object, which can be imported and run in any Python file in the same directory.  

The object has three main functions:

#### scraper = LIScraper(ref_path)
Arguments:
+ ref_path: the path of the text file containing your information. For example: *path.txt*  
  
The text file should have three lines:
* The full path of the chromedriver.exe file. For example: *C:\Users\user\chromedriver_win32\chromedriver.exe*
* Your LinkedIn username. For example: *example@school.edu*
* Your LinkedIn password. For example: *password123*

#### LIScraper.run(start_url, degrees, connects, save, csv_path, process):
Arguments:
* *start_url*: the URL of the LinkedIn profile to be started on
* *degrees*: the maximum number of degrees of separation to be considered. For example, if *degree = 1*, then the scraper will
retrieve information from the starting profile and the related profiles on the starting profile. __NOTE: for visualization purposes, 
the maxmimum number of degrees supported is 5__.
* *connects*: the maximum number of related profiles to retrieve for each profile. For example, if *connects = 3*, then for each profile,
the scraper will add 3 related profiles from that profile to the queue
* *save*: if True, the scraper will automatically save the DataFrame as a csv file
* *csv_path:* path specifying where the DataFrame should be saved to. For example, if *csv_path = profiles.csv*, the scraped data
will be saved as a csv file called profiles
* *process*: if True, after scraping is complete, profiles in the DataFrame without profile pictures will be given a default
picture and all profiles will be assigned a graph_degree value.  

This function does the actual scraping. Since the scraper uses Selenium to access webpages, it is relatively slow -- the speed is determined mostly by your browser and Internet speed.
Start at the starting profile, the scraper will scrape information related to the person's job, education, and experience before
adding the related profiles under the "People also viewed" section to the queue. The process repeats until profiles that are *degree*
degrees away from the starting profile are reached; at this point, no additional profiles will be added to the queue. __Note: this is only 
a very shallow summary of the scraper. For more details and information about its restrictions, see the first few paragraphs in the *scraper.ipynb* file.__

#### LIScraper.save(csv_path)
Arguments:
* *csv_path*: the path specifying where DataFrame should be saved. For example: "profiles.csv"  
  
If save = False when LIScraper.run() is called, then this function can be run to manually save the DataFrame.  
  

### vis.py
This file contains functions that create a graph and tree visualizations for the scraped data. It should be run from the Terminal
with the syntax:
+ *python vis.py [csv file containing the scraped profile data] [graph/tree] [name of the outputted visualization]*  
  + If *graph* is specified, then an undirected graph showing all connections between profiles is created  
  + If *tree* is specified, then a hierarchical tree model representing how the scraper processed profiles is created  
  + Example: *python vis.py profiles.csv graph profiles_graph*
    + This command will create a graph with the data in the profiles.csv file and save the graph as *profiles_graph.html*
  

## Data dictionary
Every outputted csv file containing scraped profile information has the following attributes:
+ *source_id*: the id of the profile on from which this profile was retrieved
+ *dest_id*: this profile's id
+ *dest_name*: this profile's name
+ *dest_title*: this profile's most recent job title
+ *dest_company*: this profile's most recent company
+ *dest_location*: this profile's most recent location
+ *dest_school*: this profile's most recently attended school
+ *dest_pic*: this profile's profile picture OR a default profile picture
+ *dest_childs*: the ids of ALL PROFILES under this profile's "People also viewed" tab
+ *tree_degree*: the depth of this profile in the tree visualization
+ *dest_connected*: the ids of all profiles WITHIN THIS DATASET to which this profile is connected 
+ *graph_degree*: the degree of separation of this profile from the starting profile in the graph visualization

## Additional information about files in this repo

### scraper.ipynb vs scraper.py
The scraper.ipynb file is mostly informational. If you would like to make changes to the scraper's code, please edit the scraper.py file instead -- the code in the scraper.py file is the code that is ultimately used.

### run_scraper_ap.ipynb, run_scraper_cc.ipynb
These are examples of the scraper being run. 

### .csv files
These are the datasets outputted by running the scraper on the two example profiles.

### .html files
These are the visualizations generated using the datasets from running the scraper on the two example profiles
