from flask import Flask
from flask import request
import json
from utils import (
    getAllUsers,
    validateUsernameInput,
    validateNewUsername,
    createUser,
    checkUsernameExistence,
    getUser,
    deleteUser,
    checkUsernameExistence,
    handleMessages,
    handleReadStatus
)

app = Flask(__name__)

@app.route("/")
def homeRoute():
    return "Welcome to the text messaging service.", 200

# GET:  For admin to check all users in mock db.
# POST: For new users to create account.
@app.route("/users", methods=["GET", "POST"])
def allUsersRoute():
    if request.method == "GET":
        [response, statusCode, header] = getAllUsers()
    elif request.method == "POST":
        [response, statusCode, username] = validateUsernameInput()
        if statusCode != 200:
            return response, statusCode

        [response, statusCode] = validateNewUsername(username)
        if statusCode != 200:
            return response, statusCode

        [response, statusCode, header] = createUser(username)
    return response, statusCode, header

# GET:    For admin to get data of specific user.
#         For user to see his/her own account data.
# DELETE: For user to delete his/her own account.
@app.route("/users/<string:username>", methods=["GET", "DELETE"])
def specficUserRoute(username):
    [response, statusCode] = checkUsernameExistence(username, "user")
    if statusCode != 200:
        return response, statusCode

    with open("./mock_db/users.json", "r+") as f:
        data = json.load(f)
        if request.method == "GET":
            [response, statusCode] = getUser(username, data)
        elif request.method == "DELETE":
            [response, statusCode, newData] = deleteUser(username, data)
            f.truncate(0)
            f.seek(0)
            f.write(json.dumps(newData, indent=4))
    return response, statusCode

# For admin to check all messages in mock db.
@app.route("/messages")
def allMessagesRoute():
    with open("./mock_db/messages.json", "r") as f:
        allMessages = json.load(f)
        return allMessages, 200

# GET:    For user to see all messages, both read and unread ones.
# POST:   For user to send message to recipient.
# DELETE: For user to delete message(s).
@app.route("/messages/<string:username>", methods=["GET", "POST", "DELETE"])
def userMessagesRoute(username):
    [response, statusCode] = checkUsernameExistence(username, "user")
    if statusCode != 200:
        return response, statusCode

    response = handleMessages(username)
    if request.method == "GET":
        handleReadStatus(username)
    return response

app.run(debug=True)
