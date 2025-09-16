from api.common.helpers import load_dict, save_dict

import uuid


class OperationDao:
    # def __init__(self):
    #     pass

    def get_operation_uuid(self):
        return uuid.uuid4().hex

    def get_operation_from_db(self, id):
        operation_dict = load_dict("api/data/operation_dict.npy")
        return operation_dict.get(id)

    def put_operation_into_db(self, operation_repr):
        operation_dict = load_dict("api/data/operation_dict.npy")
        operation_dict[operation_repr["id"]] = operation_repr
        save_dict(operation_dict, "api/data/operation_dict.npy")
        return True

    def update_operation_in_db(self, operation_repr):
        operation_dict = load_dict("api/data/operation_dict.npy")
        operation_dict[operation_repr["id"]] = operation_repr
        save_dict(operation_dict, "api/data/operation_dict.npy")
        return True

    def delete_operation_from_db(self, bucket_obj, uri):
        operation_dict = load_dict("api/data/operation_dict.npy")
        operation_dict.pop(uri)
        bucket_obj.pop(bucket_obj.index(uri))
        save_dict(operation_dict, "api/data/operation_dict.npy")
        return True
