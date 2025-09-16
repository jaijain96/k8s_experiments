"""
defines object resource
"""
from flask import request, Response
from flask.views import MethodView

from api.daos.user_dao import UserDao
from api.daos.object_dao import ObjectDao
from api.daos.bucket_dao import BucketDao

import json


class ObjectView(MethodView):
    def __init__(self):
        self.name_key = "object_view"
        self.user_dao = UserDao()
        self.object_dao = ObjectDao()
        self.bucket_dao = BucketDao()

    def get(self, bucket_name, object_uri):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        bucket_obj = self.bucket_dao.get_bucket_from_db(bucket_name)
        if bucket_obj is None:
            return Response(response=f"bucket {bucket_name} doesn't exist", status=404)

        object_obj = self.object_dao.get_object_from_db(object_uri)
        if object_obj is None:
            return Response(response=f"{bucket_name}/{object_uri} doesn't exist", status=404)
        return {f"{bucket_name}/{object_uri}": object_obj}

    def put(self, bucket_name, object_uri):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        bucket_obj = self.bucket_dao.get_bucket_from_db(bucket_name)
        if bucket_obj is None:
            return Response(response=f"bucket {bucket_name} doesn't exist", status=404)

        object_obj = self.object_dao.get_object_from_db(object_uri)
        if object_obj is not None:
            return Response(response=f"{bucket_name}/{object_uri} already exists", status=409)

        object_repr = request_data["repr"]
        self.object_dao.put_object_into_db(bucket_obj, object_uri, object_repr)
        self.bucket_dao.update_bucket_in_db(bucket_name, bucket_obj)
        return Response(response=json.dumps({"object created": f"{bucket_name}/{object_uri}"}), status=201)

    def patch(self, bucket_name, object_uri):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response="user doesn't exist", status=404)

        bucket_obj = self.bucket_dao.get_bucket_from_db(bucket_name)
        if bucket_obj is None:
            return Response(response=f"bucket {bucket_name} doesn't exist", status=404)

        object_obj = self.object_dao.get_object_from_db(object_uri)
        if object_obj is None:
            return Response(response=f"{bucket_name}/{object_uri} doesn't exist", status=404)

        object_repr = request_data["repr"]
        self.object_dao.update_object_in_db(object_uri, object_repr)
        return {"object updated": f"{bucket_name}/{object_uri}"}

    def delete(self, bucket_name, object_uri):
        request_data = request.get_json()
        user_id = request_data["user_id"]
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response="user doesn't exist", status=404)

        bucket_obj = self.bucket_dao.get_bucket_from_db(bucket_name)
        if bucket_obj is None:
            return Response(response=f"bucket {bucket_name} doesn't exist", status=404)

        object_obj = self.object_dao.get_object_from_db(object_uri)
        if object_obj is None:
            return Response(response=f"{bucket_name}/{object_uri} doesn't exist", status=404)

        self.object_dao.delete_object_from_db(bucket_obj, object_uri)
        self.bucket_dao.update_bucket_in_db(bucket_name, bucket_obj)
        return {"object deleted": object_uri}
