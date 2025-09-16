from api.common.helpers import load_dict, save_dict


class UserDao:
    # def __init__(self):
    #     pass

    def get_user_from_db(self, id):
        user_dict = load_dict("api/data/user_dict.npy")
        return user_dict.get(id)

    def put_user_into_db(self, id, data):
        user_dict = load_dict("api/data/user_dict.npy")
        user_dict[id] = data
        save_dict(user_dict, "api/data/user_dict.npy")
        return True

    def update_user_in_db(self, id, name):
        user_dict = load_dict("api/data/user_dict.npy")
        user_dict[id]["name"] = name
        save_dict(user_dict, "api/data/user_dict.npy")
        return True

    def delete_user_from_db(self, id):
        user_dict = load_dict("api/data/user_dict.npy")
        user_dict.pop(id)
        save_dict(user_dict, "api/data/user_dict.npy")
        return True
