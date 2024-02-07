import shelve

def get_response(text, user):
    text = str(text).strip()

    if text.isdigit() and 1 <= int(text) <= 5:
        response = validate_questions(text)
        return response
    else:
        store_user_message(user, text)
        return "Thanks for your question, referring you to admin."

def validate_questions(question):
    question = question.replace(" ", "")
    if question.isdigit() and 1 <= int(question) <= 5:
        question = int(question)
        if question == 1:
            return "Under the \"Listings\" page, you should be able to buy or rent products of your choice."
        elif question == 2:
            return "We operate at 259 Bishan"
        elif question == 3:
            return "You can navigate to the \"Reports\" page to file a report against someone."
        elif question == 4:
            return "Ensure that all code is integrated seamlessly, with functionality and usability."
        else:
            return "The one, the only, Matthias Seah Hao Jun."
    else:
        return False

def store_user_message(user, message):
    with shelve.open("user_messages_db") as user_messages_db:
        user_messages = user_messages_db.get("user_messages", {})

        # If the user already exists, append the message to the existing list
        if user in user_messages:
            user_messages[user].append(message)
        else:
            # If the user doesn't exist, create a new list with the message
            user_messages[user] = [message]

        user_messages_db["user_messages"] = user_messages

def get_user_messages():
    with shelve.open("user_messages_db") as user_messages_db:
        return user_messages_db.get("user_messages", {})