"""
defines user resource
"""
from flask import request, Response
from flask.views import MethodView

from api.daos.user_dao import UserDao
from api.daos.bucket_list_dao import BucketListDao

import json


class UserView(MethodView):
    def __init__(self):
        self.name_key = "user_view"
        self.user_dao = UserDao()
        self.bucket_list_dao = BucketListDao()

    def get(self, user_id):
        user_obj = self.user_dao.get_user_from_db(
            user_id
        )  # can use pydantic for request json parsing for type checks etc.
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        return {"user": user_obj}

    def put(self, user_id):
        request_data = request.get_json()

        user_obj = self.user_dao.get_user_from_db(user_id)
        if user_obj:
            return Response(
                response=f"user {user_id} already exists",
                status=409,  # 409: conflict
            )

        user_repr = {"name": request_data["name"]}
        self.user_dao.put_user_into_db(user_id, user_repr)

        self.bucket_list_dao.put_bucket_list_into_db(user_id, [])
        return Response(
            response=json.dumps({"user created": user_repr}),
            status=201,  # 201: created
        )

    def patch(self, user_id):
        request_data = request.get_json()

        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        self.user_dao.update_user_in_db(user_id, request_data["name"])
        return {"user": user_obj}

    def delete(self, user_id):
        user_obj = self.user_dao.get_user_from_db(user_id)
        if not user_obj:
            return Response(response=f"user {user_id} doesn't exist", status=404)

        self.bucket_list_dao.delete_bucket_list_from_db(user_id)
        self.user_dao.delete_user_from_db(user_id)
        return {"user": user_obj}
