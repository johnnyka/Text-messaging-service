# Text message service
A backend text messaging service using REST API and Python.
## Table of contents
* [Description](#description)
* [Technologies used](#technologies-used)
* [Installation](#installation)
* [Usage](#usage)
* [Selected example responses](#selected-example-responses)
* [Future developments/improvements](#future-developments/improvements)

## Description
This task was given by [&lt;/salt>](https://salt.study/) as a coding test.
The instructions were to build a service for sending and retrieving text messages using REST API and Python with the following functionalities:
* Submit a message to a defined recipient
* Fetch previously not fetched messages
* Delete one or more messages
* Fetch messages (including previously fetched) ordered by time, according to start and stop index

Furthermore
* A client interface was not required
* Authorization or authentication was not required
* No mentioning of database implementation

Since I didn't have a contact person, I did some assumptions/choices:
* The recipient will be defined with a username
* Previously not fetched messages is interpreted as unread messages
* The start and stop indices for fetching messages ordered by time will be specified as ```from``` and ```to``` dates: YYYYY-MM-DD
* The messages are listed in descending order based on the date
* The user data and messages will be stored in a mock database, in the form of a json file containing a list of dictionaries
* The requests will be responded with strings (for messages) and json objects (for user data or messages)
* Some basic error handling in case the user gives the wrong input

## Technologies used
* <a href="https://www.python.org/" title="Python"><img src="https://github.com/tomchen/stack-icons/blob/master/logos/python.svg" alt="Python" width="30px" height="30px"></img> Python 3.7.7</a>
* <a href="https://flask.palletsprojects.com/en/1.1.x/" title="Flask"><img src="https://github.com/tomchen/stack-icons/blob/master/logos/flask.svg" alt="Flask" width="30px" height="30px"></img>Flask 1.1.2</a> 

## Installation
Make sure you have installed the technologies above on you machine.

## Usage
To run the app in development mode, write the following in the terminal:
```
export FLASK_APP=app.py
export FLASK_ENV=development
python3 -m flask run
```
Suggested to use curl for sending HTTP requests.

### The ```home``` route
```curl -X GET http://localhost:5000```

### The ```users``` route
For admin to check all users data: <br>
```curl -X GET http://localhost:5000/users```

For new users to create a new account: <br>
```curl -X POST -i -d "username=YOUR_UNIQUE_USERNAME" http://localhost:5000/users```

### The ```users/USERNAME``` route
To check data of specific user: <br>
```curl -X GET http://localhost:5000/users/YOUR_UNIQUE_USERNAME```

For a user to delete his/her own account (messages will not be deleted): <br>
```curl -X DELETE -i http://localhost:5000/users/YOUR_UNIQUE_USERNAME```

### The ```messages``` route
For admin to check all messages: <br>
```curl -X GET http://localhost:5000/messages```

### The ```messages/USERNAME```route
For user to check unread messages: <br>
```curl -X GET http://localhost:5000/messages/YOUR_UNIQUE_USERNAME```

For user to check messages (both read and unread) in a given time period (in this example from 2020-08-01 to 2020-08-20): <br>
```curl -X GET "http://localhost:5000/messages/YOUR_UNIQUE_USERNAME?from=2020-08-01&to=2020-08-20"```

For user to send a new message: <br>
```curl -X POST -d "to=YOUR_RECIPIENT&message=YOUR_MESSAGE" http://localhost:5000/messages/YOUR_UNIQUE_USERNAME```

For user to delete his/her own message(s) (Note that the message IDs are in the format of uuid, see example responses below. Also note that several message IDs are comma separated): <br>
```curl -X DELETE -i -d "id=MESSAGE_ID_1, MESSAGE_ID_2" http://localhost:5000/messages/YOUR_UNIQUE_USERNAME```

## Selected example responses

### Specific user data 
```curl -X GET http://localhost:5000/users/sarasmith```
```
{
  "created": "2020-07-11 09:46:24.916432", 
  "id": "12345678-1234-1234-1234-123456789013", 
  "username": "sarasmith"
}
```

### Create new user account
```curl -X POST -i -d "username=johndoe" http://localhost:5000/users```
```
HTTP/1.0 201 CREATED
Location: http://localhost:5000/johndoe
Content-Type: text/html; charset=utf-8
Content-Length: 38
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Tue, 11 Aug 2020 08:18:26 GMT

New user account successfully created.
```

### Unread messages
```curl -X GET http://localhost:5000/messages/sarasmith```
```
{
  "Unread": [
    {
      "date": "2020-08-11 11:49:25.336470", 
      "from": "harryblack", 
      "id": "43103d93-9398-4caf-9202-e0ffbfd72db7", 
      "message": "How are you?", 
      "read": false, 
      "to": "sarasmith"
    }
  ]
}
```

...the next time the user sends the same GET request there won't be any unread messages (given that any new messages have not been received):

```curl -X GET http://localhost:5000/messages/sarasmith```
```
You have no unread messages.
```

### Messages in a given time period
```curl -X GET "http://localhost:5000/messages/sarasmith?from=2020-08-01&to=2020-08-20"```
```
{
  "messages": [
    {
      "date": "2020-08-11 11:49:25.336470", 
      "from": "harryblack", 
      "id": "43103d93-9398-4caf-9202-e0ffbfd72db7", 
      "message": "How are you?", 
      "read": false, 
      "to": "sarasmith"
    }, 
    {
      "date": "2020-08-11 11:49:22.332011", 
      "from": "harryblack", 
      "id": "57c5d8a6-07ae-487b-b31a-46686a912993", 
      "message": "Hi Sara.", 
      "read": true, 
      "to": "sarasmith"
    }, 
    {
      "date": "2020-08-08 00:04:35.914704", 
      "from": "johndoe", 
      "id": "384e3bc6-2cc2-464b-9f93-1b28a3ec3da1", 
      "message": "Sounds good. Let's keep in touch.", 
      "read": true, 
      "to": "sarasmith"
    }, 
    {
      "date": "2020-08-07 23:08:17.936505", 
      "from": "johndoe", 
      "id": "542bb40b-0f33-4f8a-aceb-e9763a300746", 
      "message": "Hi Sara! Long time no see. How are you nowadays?", 
      "read": true, 
      "to": "sarasmith"
    }
  ]
}
```
### Delete message(s)
```curl -X DELETE -i -d "id=36a6ca7d-c81b-49c2-bee5-8155bbecaa55, b3e22872-6bee-4c5c-a8a0-3d4993218ffe" http://localhost:5000/messages/sarasmith```
```
HTTP/1.0 204 NO CONTENT
Content-Type: text/html; charset=utf-8
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Tue, 11 Aug 2020 08:44:04 GMT
```

## Future developments/improvements
* Client interface such as html pages with forms --> User friendliness
* Login (authentication & authorization) --> Security and privacy
* Database for storage of user data and messages --> Scalability
* Unit tests --> Documentation and facilitation of further development
