from pymongo import MongoClient


uri = "mongodb+srv://kopal:isaac1023@cluster0.tsyn9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)


db = client['joy-plant-disease']



def check_password(encrypted, test: str):

    return encrypted == test


def login(email, password):

    user = db['users'].find_one({'email': email})

    if not user:

        return None

    if not check_password(user['password'], password):
        return None

    user.pop('_id')
    user.pop('password')

    if 'role' not in user:
        user['role'] = 'user'

    print("Role", user)
    return user


def edit_profile(email, data) -> bool:

    db['users'].update_one(
        {'email': email},
        {'$set': data}
    )

    return True


def signup(**user_details):

    if 'role' not in user_details:
        user_details['role'] = 'user'

    db['users'].insert_one(user_details)
    return True


def get_results(collection='results'):

    return list(db[collection].find({}, {'_id': 0}))


def register_results(data, collection='results'):

    db[collection].insert_one(data)
    return True
