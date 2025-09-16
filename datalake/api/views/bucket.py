"""
defines bucket resource
"""
from flask import request, Response
from flask.views import MethodView
from api.daos.user_dao import UserDao
from api.daos.bucket_dao import BucketDao
from api.daos.bucket_list_dao import BucketListDao
import json


class BucketView(MethodView):
    def __init__(self):
        self.name_key = "bucket_view"
        self.user_dao = UserDao()
        self.bucket_dao = BucketDao()
        self.bucket_list_dao = BucketListDao()

    def get(self, bucket_name):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        obj_list = self.bucket_dao.get_bucket_from_db(bucket_name)
        if obj_list is None:
            return Response(response=f"bucket {bucket_name} doesn't exist", status=404)

        return {bucket_name: obj_list}

    def put(self, bucket_name):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        bucket_list = self.bucket_list_dao.get_bucket_list_from_db(user_id)
        if bucket_name in bucket_list:
            return Response(
                response=f"bucket {bucket_name} already exists", status=409
            )

        bucket_obj = self.bucket_dao.get_bucket_from_db(bucket_name)
        if bucket_obj is not None:
            return Response(
                response=f"bucket {bucket_name} already exists", status=404
            )

        self.bucket_dao.put_bucket_into_db(bucket_list, bucket_name)
        self.bucket_list_dao.update_bucket_list_in_db(user_id, bucket_list)
        return Response(
            response=json.dumps({"bucket created": bucket_name}), status=201
        )

    # def patch(self):
    #     request_data = request.get_json()
    #     bucket_obj = self.bucket_dao.get_bucket_from_db(request_data["id"])
    #     if not bucket_obj:
    #         return Response(response="user doesn't exist", status=404)

    #     bucket_obj["name"] = request_data["name"]
    #     return {"bucket updated": bucket_obj}

    def delete(self, bucket_name):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        bucket_list = self.bucket_list_dao.get_bucket_list_from_db(user_id)
        if bucket_name not in bucket_list:
            return Response(
                response=f"bucket {bucket_name} doesn't exist", status=404
            )

        bucket_obj = self.bucket_dao.get_bucket_from_db(bucket_name)
        if bucket_obj is None:
            return Response(
                response=f"bucket {bucket_name} doesn't exist", status=404
            )

        self.bucket_dao.delete_bucket_from_db(bucket_list, bucket_name)
        self.bucket_list_dao.update_bucket_list_in_db(user_id, bucket_list)
        return {f"bucket {bucket_name} deleted": bucket_obj}
