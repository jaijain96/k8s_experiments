"""
defines bucket_list resource
"""
from flask import request, Response
from flask.views import MethodView
from api.daos.user_dao import UserDao
from api.daos.bucket_dao import BucketDao
from api.daos.bucket_list_dao import BucketListDao
import json


class BucketListView(MethodView):
    def __init__(self):
        self.name_key = "bucket_list_view"
        self.user_dao = UserDao()
        self.bucket_dao = BucketDao()
        self.bucket_list_dao = BucketListDao()

    def get(self):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        bucket_list = self.bucket_list_dao.get_bucket_list_from_db(user_id)
        return {"bucket_list": bucket_list}

    # def put(self):
    #     return {self.name_key: "put called"}

    # def patch(self):
    #     return {self.name_key: "patch called"}

    # def delete(self):
    #     return {self.name_key: "delete called"}

    def post(self):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        bucket_list = self.bucket_list_dao.get_bucket_list_from_db(user_id)
        bucket_name = request_data["bucket_name"]
        if bucket_name in bucket_list:
            return Response(response=f"bucket {bucket_name} already exists", status=409)

        self.bucket_dao.put_bucket_into_db(bucket_list, bucket_name)
        self.bucket_list_dao.update_bucket_list_in_db(user_id, bucket_list)
        return Response(
            response=json.dumps({"bucket created": bucket_name}), status=201
        )
