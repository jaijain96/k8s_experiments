from flask import Flask
from api.views.user import UserView
from api.views.bucket import BucketView
from api.views.bucket_list import BucketListView
from api.views.object import ObjectView
from api.views.operation import OperationView
from api.views.operation_create import OperationCreateView


def create_app(test_config=None):
    flask_app = Flask(__name__)
    flask_app.add_url_rule("/user/<user_id>", view_func=UserView.as_view("user_view"))
    flask_app.add_url_rule(
        "/bucket/<bucket_name>", view_func=BucketView.as_view("bucket_view")
    )
    flask_app.add_url_rule(
        "/bucket_list", view_func=BucketListView.as_view("bucket_list_view")
    )
    flask_app.add_url_rule(
        "/<bucket_name>/<object_uri>", view_func=ObjectView.as_view("object_view")
    )
    flask_app.add_url_rule(
        "/operation", view_func=OperationCreateView.as_view("operation_create_view")
    )
    flask_app.add_url_rule(
        "/operation/<id>", view_func=OperationView.as_view("operation_view")
    )

    return flask_app
