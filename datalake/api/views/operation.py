"""
defines operation resource
"""
from flask import request, Response
from flask.views import MethodView
import json

from api.daos.user_dao import UserDao
from api.daos.object_dao import ObjectDao
from api.daos.bucket_dao import BucketDao
from api.daos.operation_dao import OperationDao


class OperationView(MethodView):
    def __init__(self):
        self.name_key = "operation_view"
        self.user_dao = UserDao()
        self.object_dao = ObjectDao()
        self.bucket_dao = BucketDao()
        self.operation_dao = OperationDao()

    def get(self, id):
        return {self.name_key: "get called"}

    def patch(self, id):
        return {self.name_key: "patch called"}

    def delete(self, id):
        return {self.name_key: "delete called"}
