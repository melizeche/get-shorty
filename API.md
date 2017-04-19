**create**
----
  _Create a shortened URL._

* **URL**

  _/api/1.0/create_

* **Method:**
  
  `POST`

* **Data Params**
  JSON payload

    **Required:**
   `url=[string]`

    **Optional:**
   `url-mobile=[string]`
   `url-tablet=[string]`
* **Success Response:**
  
  * **Code:** 201
    **Content:** `{"shorten": "http://localhost:5000/6"}`
 
* **Error Response:**

  * **Code:** 422 UNPROCESSABLE ENTITY
    **Content:** `{"errors": [{"error": "missing parameter","detail": "url parameter is mandatory"}}`
  * **Code:** 422 UNPROCESSABLE ENTITY
    **Content:** `{"errors": [{'error': 'invalid url','detail': 'Invalid url, make sure to add the protocol e.g. http://'}]}`
  * **Code:** 422 UNPROCESSABLE ENTITY
    **Content:** `{"errors": [{'error': 'invalid url-mobile','detail': 'Invalid url url-mobile, make sure to add the protocol e.g. http://'}]}`
  * **Code:** 422 UNPROCESSABLE ENTITY
    **Content:** `{"errors": [{'error': 'invalid url-tablet','detail': 'Invalid url url-tablet, make sure to add the protocol e.g. http://'}]}`

  OR

  * **Code:** 500  Internal Server Error
    **Content:** `{"errors": [{'error': 'server error','detail': 'Server Error'}]}`
* **Sample Call:**

    `curl -d '{"url":"https://www.facebook.com","url-mobile":"https://m.facebook.com/","url-tablet":"https://touch.facebook.com/"}' localhost:5000/api/1.0/create`

* **Notes:**


**list**
----
  _Lists all the urls along with the targets and redirects count._

* **URL**

  _/api/1.0/list_

* **Method:**
  
  `GET`

* **Success Response:**
  
  * **Code:** 200
    **Content:** `[
{
id: 1,
short: "http://localhost:5000/vc3",
default_url: "http://www.facebook.com",
default_hits: 4,
mobile_url: "http://m.facebook.com",
mobile_hits: 20,
tablet_url: "http://touch.facebook.com",
tablet_hits: 1,
created: "2017-04-19 08:45:07"
},
{
id: 2,
short: "http://localhost:5000/2",
default_url: "http://google.com",
default_hits: 45,
mobile_url: "http://melizeche.com",
mobile_hits: 30,
tablet_url: "http://youtube.com",
tablet_hits: 2,
created: "2017-04-19 09:31:12"
}]`
 
* **Error Response:**

  * **Code:** 500  Internal Server Error
    **Content:** `{"errors": [{'error': 'server error','detail': 'Server Error'}]}`
* **Sample Call:**

    `curl localhost:5000/api/1.0/list`

* **Notes:**



