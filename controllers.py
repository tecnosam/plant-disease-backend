from pymongo import MongoClient


client = MongoClient()


db = client['sarah-brain-tumor-detector']



def check_password(encrypted, test: str):

    return encrypted == test


def login(email, password):

    user = db['users'].find_one({'email': email})

    if not user:

        return False

    return check_password(user['password'], password)


def signup(**user_details):

    db['users'].insert_one(user_details)
    return True


def get_results():

    return list(db['results'].find({}, {'_id': 0}))


def register_results(data):

    db['results'].insert_one(data)
    return True
