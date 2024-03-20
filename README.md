# Lazy reposync using Web Scraping
A basic lazy implementation of the Uyuni's [reposync](https://github.com/uyuni-project/uyuni/blob/master/python/spacewalk/satellite_tools/reposync.py) component using web scraping.
This service is only implementing the packages' metadata fetch process.

## Main Idea
The main idea of the lazy reposync service is to fetch packages' metadata directly from the remote repositories without downlodaing the packages and extracting the corresponding metadata from these packages.
So we'll be scrapping the remote pacakge's repository's website to extract pakages metadata, and then save these metadata into a local Postgres db.


## How does it work ?
The following flowchart diagram might give an idea on the general lazy reposync service:

![scrape-md drawio](https://github.com/waterflow80/lzreposync-wb-scraping/assets/82417779/b5f1b287-231a-4777-9846-3c60b194ebde)


## Persistence 
The fetched metadata will be stored in a local Postgres database in a table called `package_meta_data`. Here's a portion of the content of that table after 
fetching some packges' metadata using the `lzrzposync`:
| pkg_name | pkg_version | pkg_description | pkg_repository | 
|--|--|--|--|
| abook                         | (0.6.1-1build4)       | text-based ncurses address book application                | [universe] |
| addresses-goodies-for-gnustep | (0.4.8-3build2)       | Personal Address Manager for GNUstep (Goodies)             | [universe] | 
| addressmanager.app            | (0.4.8-3build2)       | Personal Address Manager for GNUstep                       | [universe] |
| akonadi-import-wizard         | (4:19.12.3-0ubuntu1)  | PIM data import wizard                                     | [universe] |
| alot                          | (0.9-1)               | Text mode MUA using notmuch mail                           | [universe] |


## Run
To setup and run the `lzreposync` service locally, please follow these steps:
```shell
$ git clone https://github.com/waterflow80/lzreposync-wb-scraping.git
$ cd lzreposync
$ docker-compose up (preferably in another terminal)
$ pip install -r requirements.txt # note some libraries in this file are not necessary and should have been removed.
$ python3.8 lzreposync # if you notice an error like `psycopg2.errors.SyntaxError: ... don't worry, it's just sql complaining, we haven't completed formatting yet

# Now we can see the metadata saved into our database
$ docker exec -it db bash
$ psql -U postgres -d DB
$ SELECT * FROM package_meta_data; # You should see the metadata saved in the datatabase

` 
```

## Current Limitations
The current service is only a small implementation used for demonstration purposes, so the service will work for the following parameters:
- Looking for packges in the **Ubuntu Packages** [repository](https://packages.ubuntu.com/)
- Lokking for packages under the **focal** Linux distro
- Looking gor packages under the **Main** subsection

Some functions still miss some exception handling and some formatting, as we've said this is just for demonstration purposes.
