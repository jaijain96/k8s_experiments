from api.common.helpers import load_dict, save_dict


class ObjectDao:
    # def __init__(self):
    #     pass

    def get_object_from_db(self, uri):
        object_dict = load_dict("api/data/object_dict.npy")
        return object_dict.get(uri)

    def put_object_into_db(self, bucket_obj, uri, obj_repr):
        object_dict = load_dict("api/data/object_dict.npy")
        object_dict[uri] = obj_repr
        bucket_obj.append(uri)
        save_dict(object_dict, "api/data/object_dict.npy")
        return True

    def update_object_in_db(self, uri, obj_repr):
        object_dict = load_dict("api/data/object_dict.npy")
        object_dict[uri] = obj_repr
        save_dict(object_dict, "api/data/object_dict.npy")
        return True

    def delete_object_from_db(self, bucket_obj, uri):
        object_dict = load_dict("api/data/object_dict.npy")
        object_dict.pop(uri)
        bucket_obj.pop(bucket_obj.index(uri))
        save_dict(object_dict, "api/data/object_dict.npy")
        return True
