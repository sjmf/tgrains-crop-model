# Crop Model API Routes

### [/ (index)](/)
_Method:_ `GET`   
Return this help string


### [/test](/test)
_Method:_ `GET`

**FLASK_ENV=development ONLY** 

Returns a HTML test form which can be used to POST values to the `/model` endpoint.


### [/echo](/echo)
_Method:_ `POST`

**FLASK_ENV=development ONLY** 

Echos whatever POST request it received back at the browser. 


### [/strings](/strings?landscape_id=101)
_Method:_ `GET`

Get the list of crop and livestock strings. Takes a variable for landscape ID, e.g.:

`GET /strings?landscape_id=101`


### [/model](/model?landscape_id=101)
_Method:_ `GET`

Get the BAU (Business as usual) state. Takes a variable for landscape ID, e.g.:

`GET /model?landscape_id=101`

Valid landscape IDs are currently 101, 102.


### [/model](/model)
_Method:_ `POST`

Post variables to the model for response. POST body MUST include all the below variables, formatted as JSON. Values 
(with the exception of `landscape_id`, an integer) are in hectares and will be interpreted as float-point numbers.

* landscape_id = 101
* (Crop and livestock variables, which are now retrieved via [/strings](strings?landscape_id=101))


### [/comment](/comment?page=1&size=10)
_Method:_ `GET`

Get comments from the database in paginated form. The following params control the pagination:

* page: Integer. The page to load.
* size: Integer. The size of a page.

Comments are returned as JSON.

NB: Page counter starts at 1. Requesting page 0 results in 404 not found (from flask-sqlalchemy)


### [/comment](/comment?page=1&size=10)
_Method:_ `POST`

Post a comment to the model, to be stored in the database. POST body MUST include the below variables, formatted as 
JSON. 

* text: String. The comment body.
* author: String. The author's name.
* email: String. The author's email address (may be NULL for social medial login)

POST body MAY also include the following variable:

* reply_id: Integer. The comment that this comment is replying to.


### [/tags](/tags)
_Method:_ `GET`

Retrieve comment tags from the database.
