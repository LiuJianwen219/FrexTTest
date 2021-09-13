import json
import requests
import logging
from Constant import constants as const

logger = logging.getLogger(__name__)


def post_questions(values, file):
    logger.info("Try to post QUESTION with values: " + json.dumps(values))

    url = const.file_server_url + const.questions_API + "/"
    values = {
        const.c_testId: values[const.c_testId],
        const.c_topic: values[const.c_topic]
    }

    files = {'file': file}
    r = requests.post(url, files=files, data=values)
    if r.status_code.__str__() != "200":
        logger.error("Post QUESTION failed: request status not health: " + r.headers.__str__())
        return const.request_failed
    return const.request_success


def post_test(values, file):
    logger.info("Try to post TEST with values: " + json.dumps(values))

    url = const.file_server_url + const.tests_API + "/"
    values = {
        const.c_userId: values[const.c_userId],
        const.c_testId: values[const.c_testId],
        const.c_submitId: values[const.c_submitId],
        const.c_topic: values[const.c_topic]
    }

    files = {'file': file}
    r = requests.post(url, files=files, data=values)
    if r.status_code.__str__() != "200":
        logger.error("Post TEST failed: request status not health: " + r.headers.__str__())
        return const.request_failed
    return const.request_success
