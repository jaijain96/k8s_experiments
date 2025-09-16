import numpy as np


def load_dict(filepath):
    try:
        data_dict = np.load(filepath, allow_pickle=True).tolist()
        return data_dict
    except Exception as e:
        print(f"Exception occurring: {e}")
        return {}


def save_dict(data_dict, filepath):
    np.save(filepath, data_dict, allow_pickle=True)
    return True


# user_dict = load_dict("api/data/user_dict.npy")
# bucket_dict = load_dict("api/data/bucket_dict.npy")
# bucket_list_dict = load_dict("api/data/bucket_list_dict.npy")
# object_dict = load_dict("api/data/object_dict.npy")
