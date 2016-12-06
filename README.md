#Catalog

Catalog is a Udacity project Flask server to keep track of items in categories.  The site lists categories and the items within them.  New items can be created, edited and deleted.  Only items created by a user can be modified.  Google Login is supported for authentication.
  
#Prerequisites

* Python 2.7
* psycopg2 python library
* flask
* bleach
* oauth2client
* requests
* httplib2
* redis
* passlib
* itsdangerous
* flask-httpauth

To setup the prerequisites:

    $ sh pg_config.sh

Postgres should be started and running on the standard port.

#Usage

To setup the database:

    $ sh reset.sh

To run the server:

    $ sh run.sh
    
The main site is available at:

    http://localhost:5000
    
 A list of endpoints and functionalities:
 
    /
    /categories/ [GET]: list all categories and display recent items
    
    /login [GET]: login via Google
    
    /json [GET]: JSON representation of all items
    
    /category/<int:category_id> [GET]: list a category
    
    /category/json/<int:category_id> [GET]: JSON representation of a category
    
    /item/<int:item_id> [GET]: list an item
    
    /item/json/<int:item_id> [GET]: JSON representation of an item
    
    /item/new/ [POST, GET]: create an item
    
    /item/edit/<int:item_id> [POST, GET]: delete an item
    
    /item/delete/<int:item_id> [POST, GET]: delete an item

    