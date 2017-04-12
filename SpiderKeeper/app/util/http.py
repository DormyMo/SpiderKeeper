import logging

import requests


def request_get(url, retry_times=5):
    '''
    :param url:
    :param retry_times:
    :return: response obj
    '''
    for i in range(retry_times):
        try:
            res = requests.get(url)
        except Exception as e:
            logging.warning('request error retry %s' % url)
            continue
        return res


def request_post(url, data, retry_times=5):
    '''
    :param url:
    :param retry_times:
    :return: response obj
    '''
    for i in range(retry_times):
        try:
            res = requests.post(url, data)
        except Exception as e:
            logging.warning('request error retry %s' % url)
            continue
        return res


def request(request_type, url, data=None, retry_times=5, return_type="text"):
    '''

    :param request_type: get/post
    :param url:
    :param data:
    :param retry_times:
    :param return_type: text/json
    :return:
    '''
    if request_type == 'get':
        res = request_get(url, retry_times)
    if request_type == 'post':
        res = request_post(url, data, retry_times)
    if not res: return res
    if return_type == 'text': return res.text
    if return_type == 'json':
        try:
            res = res.json()
            return res
        except Exception as e:
            logging.warning('parse json error %s' % str(e))
            return None
