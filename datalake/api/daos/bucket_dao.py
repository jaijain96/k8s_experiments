from api.common.helpers import load_dict, save_dict


class BucketDao:
    # def __init__(self):
    #     pass

    def get_bucket_from_db(self, bucket_name):
        bucket_dict = load_dict("api/data/bucket_dict.npy")
        return bucket_dict.get(bucket_name)

    def put_bucket_into_db(self, bucket_list, bucket_name):
        bucket_dict = load_dict("api/data/bucket_dict.npy")
        bucket_dict[bucket_name] = []
        bucket_list.append(bucket_name)
        save_dict(bucket_dict, "api/data/bucket_dict.npy")
        return True

    def update_bucket_in_db(self, bucket_name, bucket_obj):
        bucket_dict = load_dict("api/data/bucket_dict.npy")
        bucket_dict[bucket_name] = bucket_obj
        save_dict(bucket_dict, "api/data/bucket_dict.npy")
        return True

    def delete_bucket_from_db(self, bucket_list, bucket_name):
        bucket_dict = load_dict("api/data/bucket_dict.npy")
        bucket_dict.pop(bucket_name)
        bucket_list.pop(bucket_list.index(bucket_name))
        save_dict(bucket_dict, "api/data/bucket_dict.npy")
        return True
