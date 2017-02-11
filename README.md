# Facebook-Search-in-Groups
Search in Facebook open groups for posts according to given keywords.

The script will yield the results in a HTML file.

I'm using it to automate the search for job openings in relevant faceboook groups.


## Usage:

###Edit settings.ini -

#### Create an app at:

https://developers.facebook.com/

and get your App ID and App Key.

#### Get your user access token:

https://developers.facebook.com/tools/explorer

It is required to compile a list of group IDs on the first run.

#### Set your desired words to search.

#### Add groups
Add your favorite groups in `urls` file

### Run:
The first run will yield a csv file with a list of group IDs to search in.

## CL Arguments:
search for posts since the previous day:

    main.py 
    
Search for posts since any given day:

    main.py YYYY-MM-DD

#### Use cron to run it daily.
