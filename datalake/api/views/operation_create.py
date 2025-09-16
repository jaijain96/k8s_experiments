"""
defines operation resource
"""
from flask import request
from flask.views import MethodView
from multiprocessing import Manager, Process
import asyncio, concurrent, functools, os, time

from api.daos.user_dao import UserDao

# from api.daos.object_dao import ObjectDao
# from api.daos.bucket_dao import BucketDao
from api.daos.operation_dao import OperationDao


class OperationCreateView(MethodView):
    def __init__(self):
        self.name_key = "operation_create_view"
        self.user_dao = UserDao()
        # self.object_dao = ObjectDao()
        # self.bucket_dao = BucketDao()
        self.operation_dao = OperationDao()

    def start_operation_io_intensive(self, operation_repr):
        time.sleep(5)
        operation_repr["state"] = "started"
        self.operation_dao.update_operation_in_db(operation_repr)

    # def start_operation_compute_intensive(self, operation_repr):
    #     delay = 5
    #     for idx in range(5500000 * delay):
    #         print("", end="")
    #     operation_repr["state"] = "started"
    #     self.operation_dao.update_operation_in_db(operation_repr)

    def start_operation_compute_intensive_subprocess(self, operation_repr, dict_proxy):
        print("=================started in subprocess====================")
        print(dict_proxy)
        dict_proxy[operation_repr["id"]] = os.getpid()
        print("================post appending============================")
        print(dict_proxy)
        delay = 5
        for idx in range(5500000 * delay):
            print("", end="")
        operation_repr["state"] = "started"
        print(f"process: {os.getpid()} done")
        # self.operation_dao.update_operation_in_db(operation_repr)

    def put(self):
        request_data = request.get_json()

        # validate params based on type of operation
        operation_repr = {
            "id": self.operation_dao.get_operation_uuid(),
            "type": request_data["type"],
            "state": "initiating",
            "params": request_data["params"],
        }
        # self.operation_dao.put_operation_into_db(operation_repr)
        # self.start_operation_io_intensive(operation_repr)
        # self.start_operation_compute_intensive(operation_repr)
        manager = Manager()
        dict_proxy = manager.dict()
        p = Process(
            target=self.start_operation_compute_intensive_subprocess,
            args=(operation_repr, dict_proxy),
        )
        print("=====================before start================")
        print(dict_proxy)
        p.start()
        # p.join()
        print("=================return to main process================")
        print(dict_proxy)

        # seems not reliable, but why
        # time.sleep(0.5)

        # seems less reliable, but why
        while dict_proxy.get(operation_repr["id"]) is None:
            pass

        # some other mechanism to hold this until a value has arrived? pipe, barrier or something
        return {
            "operation created": operation_repr,
            "process": dict_proxy[operation_repr["id"]],
        }

    # async def start_operation_compute_intensive_async(self, operation_repr):
    #     delay = 5
    #     for idx in range(5500000 * delay):
    #         print("", end="")
    #     operation_repr["state"] = "started"
    #     # self.operation_dao.update_operation_in_db(operation_repr)

    # async def put(self):
    #     request_data = request.get_json()

    #     # validate params based on type of operation
    #     operation_repr = {
    #         "id": self.operation_dao.get_operation_uuid(),
    #         "type": request_data["type"],
    #         "state": "initiating",
    #         "params": request_data["params"],
    #     }
    #     # self.operation_dao.put_operation_into_db(operation_repr)
    #     # self.start_operation_io_intensive(operation_repr)
    #     # self.start_operation_compute_intensive(operation_repr)
    #     # loop = asyncio.get_running_loop()
    #     # with concurrent.futures.ProcessPoolExecutor() as pool:
    #     #     loop.run_in_executor(
    #     #         pool,
    #     #         functools.partial(
    #     #             self.start_operation_compute_intensive_async, operation_repr
    #     #         ),
    #     #     )
    #     await self.start_operation_compute_intensive_async(operation_repr)

    #     return {"operation created": operation_repr}
