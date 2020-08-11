from flask import request
import json
import datetime
import uuid
import re

def getAllUsers():
    with open("./mock_db/users.json", "r") as f:
        data = json.load(f)
        return data, 200, None

def validateUsernameInput():
    try:
        username = request.form["username"]
        if username == "":
            return "The given username was empty. Please specify a username.", 400, None
    except:
        return "A username is required.", 400, None
    return "The given username is not empty.", 200, username

def checkForSpaces(username):
    if " " in username:
        return "Spaces are not allowed in the username.", 400
    return "No spaces found in username", 200

def checkUsernameClash(username):
    with open("./mock_db/users.json", "r") as f:
        data = json.load(f)
        existingUsernames = list(map(lambda user: user["username"], data["users"]))
        if username in existingUsernames:
            return "The username already exists. Try another username.", 409
    return "Username does not already exist in the db.", 200

def validateNewUsername(username):
    [response, statusCode] = checkForSpaces(username)
    if statusCode != 200:
        return response, statusCode

    [response, statusCode] = checkUsernameClash(username)
    if statusCode != 200:
        return response, statusCode

    return "Valid username.", 200

def createUser(username):
    newUser = {
        "username": username,
        "created": str(datetime.datetime.now()),
        "id": str(uuid.uuid4()),
    }
    with open("./mock_db/users.json", "r+") as f:
        data = json.load(f)
        data["users"].append(newUser)
        f.truncate(0)
        f.seek(0)
        f.write(json.dumps(data, indent = 4))
    return "New user account successfully created.", 201, {"Location": "http://localhost:5000/"+username}

def checkUsernameExistence(username, string):
    with open("./mock_db/users.json", "r") as f:
        data = json.load(f)
        existingUsernames = list(map(lambda user: user["username"], data["users"]))
        if username not in existingUsernames:
            return "The "+string+" does not exist.", 404
    return "The "+string+" exists.", 200

def getUser(username, data):
    userData = list(filter(lambda user: user["username"] == username, data["users"]))
    return userData[0], 200

def deleteUser(username, data):
    data["users"] = list(filter(lambda user: user["username"] != username, data["users"]))
    return "Successfully deleted user.", 204, data

def checkDateInputs():
    try:
        fromDate = request.args["from"]
        toDate = request.args["to"]
        
        dateRegex = re.compile(r"^[12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
        if any([dateRegex.match(fromDate) == None, dateRegex.match(toDate) == None]):
            return "'from' and 'to' needs to be in the format of YYYY-MM-DD.", 400
        return fromDate, toDate
    except:
        return "'from' and 'to' dates are required.", 400

def fetchMessagesInTimeRange(username):
    response = checkDateInputs()
    if 400 in response:
        return response
    
    [fromDate, toDate] = response
    with open("./mock_db/messages.json", "r") as f:
        data = json.load(f)
        userMessages = list(filter(lambda message: message["to"] == username, data["messages"]))
        userTimeRangeMessages = list(filter(lambda message: message["date"] >= fromDate, userMessages))
        userTimeRangeMessages = list(filter(lambda message: message["date"] <= toDate+" 23:59:59", userTimeRangeMessages))
        sortedMessages = sorted(userTimeRangeMessages, key = lambda message: message["date"], reverse = True)
        return {"messages": sortedMessages}, 200
        # readMessages = list(filter(lambda message: message["read"] == True, userTimeRangeMessages))
        # unreadMessages = list(filter(lambda message: message["read"] == False, userTimeRangeMessages))
        # return {"Unread": unreadMessages, "Read": readMessages}, 200

def fetchUnreadMessages(username):
    with open("./mock_db/messages.json", "r") as f:
        data = json.load(f)
        userMessages = list(filter(lambda message: message["to"] == username, data["messages"]))
        userUnreadMessages = list(filter(lambda message: message["read"] == False, userMessages))
        sortedUnreadMessages = sorted(userUnreadMessages, key = lambda message: message["date"], reverse = True)
        # userReadMessages = list(filter(lambda message: message["read"] == True, userMessages))
    if len(userUnreadMessages) == 0:
        return "You have no unread messages.", 200
    return {"Unread": sortedUnreadMessages}, 200

def checkPostMessageInput():
    try:
        recipient = request.form["to"]
        if recipient == "":
            return "The recipient is missing. Please specify 'to'.", 400, None, None
    except:
        return "'to' is required.", 400, None, None

    try:
        message = request.form["message"]
        if message == "":
            return "The message is empty. Please write a message.", 400, None, None
    except:
        return "'message' is required.", 400, None, None

    [response, statusCode] = checkUsernameExistence(recipient, "recipient")
    if statusCode != 200:
        return response, statusCode, None, None

    return "The message inputs are validated and accepted.", 200, recipient, message

def sendMessage(username, recipient, message):
    messageId = str(uuid.uuid4())
    messageData = {
        "from": username,
        "to": recipient,
        "id": messageId,
        "date": str(datetime.datetime.now()),
        "read": False,
        "message": message,
    }

    with open("./mock_db/messages.json", "r+") as f:
        data = json.load(f)
        data["messages"].append(messageData)
        f.truncate(0)  # Remove content in file.
        f.seek(0)  # To avoid initial symbols when writing to file.
        f.write(json.dumps(data, indent = 4))

    return messageData, 201 #, {"Location": "http://localhost:5000/"+username+"/"+messageId}

def checkIdInput():
    try:
        ids = request.form["id"]
        if ids == "":
            return "No message ID(s) was given. Please specify the message ID(s) to be deleted. Use comma separator to specify 2 or more message IDs.", 400, None
    except:
        return "'id' is required.", 400, None
    return "'id' is not empty.", 200, ids

def checkIdFormat(id):
    uuidRegex = re.compile(r"^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
    if uuidRegex.match(id) == None:
        return "The format of the message ID is incorrect. Please specify a valid uuid.", 400
    return "The format of the id(s) is correct.", 200

def checkUserMessage(username, id, messages):
    for message in messages:
        if message["id"] == id:
            if message["to"] != username:
                return "You do not have a message with the id "+id+". Please double check the message id.", 400
    return "The given message id(s) are valid and belongs to the user.", 200


def deleteMessages(username, ids):
    idsArr = ids.split(",")
    with open("./mock_db/messages.json", "r+") as f:
        data = json.load(f)
        for id in idsArr:
            strippedId = id.strip()
            [response, statusCode] = checkIdFormat(strippedId)
            if statusCode != 200:
                return response, statusCode
            
            [response, statusCode] = checkUserMessage(username, strippedId, data["messages"])
            if statusCode != 200:
                return response, statusCode

            data["messages"] = list(filter(lambda message: not all([message["to"] == username, message["id"] == strippedId]), data["messages"]))
        f.truncate(0)
        f.seek(0)
        f.write(json.dumps(data, indent = 4))
    return "Successfully deleted messages: "+ids, 204

def handleMessages(username):
    if request.method == "GET":
        if len(request.args) > 0:
            response = fetchMessagesInTimeRange(username)
            return response

        [response, statusCode] = fetchUnreadMessages(username)
        return response, statusCode

    elif request.method == "POST":
        [response, statusCode, recipient, message] = checkPostMessageInput()
        if statusCode != 200:
            return response, statusCode

        [response, statusCode] = sendMessage(username, recipient, message)
        return response, statusCode

    elif request.method == "DELETE":
        [response, statusCode, ids] = checkIdInput()
        if statusCode != 200:
            return response, statusCode
        
        [response, statusCode] = deleteMessages(username, ids)
        return response, statusCode

def updateDb(message, username):
    if message["to"] == username:
        message["read"] = True
    return message

# As soon as the user is logged in and the unread mails appear,
# the read status will be set to True. This will be evident after a refresh.
def handleReadStatus(username):
    with open("./mock_db/messages.json", "r+") as f:
        data = json.load(f)
        data["messages"] = list(map(lambda message: updateDb(message, username), data["messages"]))
        f.truncate(0)
        f.seek(0)
        f.write(json.dumps(data, indent = 4))
