import json
import warnings
from collections import OrderedDict

from restcli import yaml_utils as yaml


def parse_collection(postman_collection):
    collection = OrderedDict()
    for folder_info in postman_collection['item']:
        group_name = folder_info['name']
        collection[group_name] = parse_group(folder_info)
    return collection


def parse_group(folder_info):
    group = OrderedDict()
    for request_info in folder_info['item']:
        request_name = request_info['name']
        group[request_name] = parse_request(request_info)
    return group


def parse_request(request_info):
    request = OrderedDict()
    r = request_info['request']

    if r['description']:
        request['description'] = r['description']

    request['method'] = r['method'].lower()
    request['url'] = r['url']

    header_info = r['header']
    headers = parse_headers(header_info)
    if headers:
        request['headers'] = headers

    body_info = r['body']
    body = parse_body(body_info)
    if body:
        request['body'] = body

    return request


def parse_headers(header_info):
    py_headers = OrderedDict((h['key'], h['value']) for h in header_info)
    return yaml.dump(py_headers)


def parse_body(body_info):
    # FIXME: This interprets all literals as strings. Use the PM "type" field.
    mode = body_info['mode']
    body = body_info[mode]

    if mode == 'formdata':
        python_repr = parse_formdata(body)
    elif mode == 'raw':
        python_repr = json.loads(body)
    else:
        warnings.warn('Found unknown body mode "%s"; skipping' % mode)
        return None

    text = yaml.dump(python_repr)
    return yaml.YamlLiteralStr(text)


def parse_formdata(formdata):
    data = OrderedDict()

    for item in formdata:
        if item['type'] != 'text':
            warnings.warn('Found unknown type in formdata "%s"; skipping'
                          % item['type'])
            continue

        key = item['key']
        val = item['value']
        data[key] = val

    return data
