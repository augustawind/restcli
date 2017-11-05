import argparse
import json
import re
import sys
import warnings
from collections import OrderedDict

from restcli import yaml_utils as yaml


def parse_collection(postman_collection):
    collection = OrderedDict()
    for folder_info in postman_collection['item']:
        group_name = normalize(folder_info['name'])
        if group_name in collection:
            warnings.warn('Duplicate group name "%s"; skipping' % group_name)
        collection[group_name] = parse_group(folder_info['item'])

    return collection


def parse_group(folder_info):
    group = OrderedDict()
    for request_info in folder_info:
        request_name = normalize(request_info['name'])
        if 'item' in request_info:
            warnings.warn('Postman sub-folders are not supported; '
                          'skipping folder "%s"' % request_name)
            continue
        group[request_name] = parse_request(request_info)

    return group


def parse_request(request_info):
    request = OrderedDict()
    r = request_info['request']

    description = r.get('description')
    if description:
        request['description'] = description

    request['method'] = r['method'].lower()
    request['url'] = r['url']

    header_info = r['header']
    headers = parse_headers(header_info)
    if headers:
        request['headers'] = headers

    body_info = r['body']
    body = parse_body(body_info)
    if body and body.strip() != '{}':
        request['body'] = body

    return request


def parse_headers(header_info):
    return OrderedDict((h['key'], h['value']) for h in header_info)


def parse_body(body_info):
    # FIXME: This interprets all literals as strings. Use the PM "type" field.
    mode = body_info['mode']
    body = body_info[mode]

    if body:
        if mode == 'formdata':
            python_repr = parse_formdata(body)
        elif mode == 'raw':
            python_repr = json.loads(body)
        else:
            warnings.warn('Unsupported body mode "%s"; skipping' % mode)
            return None

        text = yaml.dump(python_repr, indent=4)
        return yaml.YamlLiteralStr(text)

    return None


def parse_formdata(formdata):
    data = OrderedDict()

    for item in formdata:
        if item['type'] != 'text':
            warnings.warn('Unsupported type in formdata "%s"; skipping'
                          % item['type'])
            continue

        key = item['key']
        val = item['value']
        data[key] = val

    return data


def normalize(text):
    text = text.lower()
    text = re.sub('\s+', '-', text)
    text = re.sub('[{}]', '', text)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('collection', type=open)
    parser.add_argument('--outfile', '-o', type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    postman_collection = json.load(args.collection)
    collection = parse_collection(postman_collection)

    output = yaml.dump(collection, indent=4)
    output = re.sub(r'^([^\s].*)$', '\n\\1', output, flags=re.MULTILINE)
    for var in re.findall(r'{{([^{}]+)}}', output):
        output = output.replace('{{%s}}' % var,
                                '{{ %s }}' % var.lower())
    print(output, file=args.outfile)


if __name__ == '__main__':
    main()
