import datetime
import json
import logging
import os
import threading
import time
import _thread

import requests
from Constant import constants as const
logger = logging.getLogger(__name__)


sim = "http://47.96.95.218:30500"
api = "/sim/get_all"


def test():
    with open("tmp/mod10.v", "r") as f:
        v_file = f.read()
    with open("tmp/mod10_test.v", "r") as f:
        v_test_file = f.read()

    print(v_file)
    print(v_test_file)

    data = {
        "testbench": v_test_file,
        "verilog": v_file,
        "runtime": 50,
    }

    response = requests.post(sim+api, data=json.dumps(data))
    print(response.content)
    di = json.loads(response.content)
    print(di['msg'])


if __name__ == "__main__":
    test()