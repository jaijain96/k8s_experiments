import hashlib

from api.common.helpers import load_dict, save_dict


class BucketListDao:
    # def __init__(self):
    #     pass

    def get_user_hash(self, user_id):
        hash_obj = hashlib.sha256()
        hash_obj.update(user_id.encode())
        return hash_obj.hexdigest()

    def get_bucket_list_from_db(self, user_id):
        bucket_list_dict = load_dict("api/data/bucket_list_dict.npy")
        return bucket_list_dict.get(self.get_user_hash(user_id))

    def put_bucket_list_into_db(self, user_id, bucket_list):
        bucket_list_dict = load_dict("api/data/bucket_list_dict.npy")
        bucket_list_dict[self.get_user_hash(user_id)] = bucket_list
        save_dict(bucket_list_dict, "api/data/bucket_list_dict.npy")
        return True

    def update_bucket_list_in_db(self, user_id, bucket_list):
        bucket_list_dict = load_dict("api/data/bucket_list_dict.npy")
        bucket_list_dict[self.get_user_hash(user_id)] = bucket_list
        save_dict(bucket_list_dict, "api/data/bucket_list_dict.npy")
        return True

    def delete_bucket_list_from_db(self, user_id):
        bucket_list_dict = load_dict("api/data/bucket_list_dict.npy")
        bucket_list_dict.pop(self.get_user_hash(user_id))
        save_dict(bucket_list_dict, "api/data/bucket_list_dict.npy")
        return True
