import json
import logging
import os

import requests
from Constant import constants as const
logger = logging.getLogger(__name__)

def file_writer(fire_dir, file_name, file_content):
    if not os.path.exists(fire_dir):
        os.makedirs(fire_dir)
    with open(os.path.join(fire_dir, file_name), 'wb+') as destination:
        destination.write(file_content)
    if len(file_content) < 1:
        return None
    return 1

def get_tests():
    userId = "1dcdba10-0d64-11ec-9d14-00d86134f158"
    testId = "412c72d4-1e80-11ec-9233-12dcc95ac57f"
    submitId = "2eede7bc-283d-11ec-bf42-1a069e0b09f6"
    topic = "mod60"
    url = const.file_server_url + "rpts" + "/"
    values = {
        const.c_userId: userId,
        const.c_testId: testId,
        const.c_submitId: submitId,
        const.c_topic: topic
    }
    r = requests.get(url, params=values)
    if r.status_code.__str__() != "200":
        logger.error("Request failed: " + r.headers.__str__())
        return const.request_failed

    if r.headers['content-type'] == "application/octet-stream" and r.content:
        dest_direction = const.work_dir
        dest_filename = topic + const.tests_suffix
        if not file_writer(dest_direction, dest_filename, r.content):
            return const.request_failed
        return const.request_success
    return const.request_failed

if __name__ == "__main__":
    get_tests()
