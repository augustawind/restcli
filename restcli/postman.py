import argparse
import json
import re
import sys
import warnings
from collections import OrderedDict

from restcli import yaml_utils as yaml

NAME_SUB_RE = re.compile(r'[{}]', re.MULTILINE)
ENV_SUB_RE = re.compile(r'{{([^{}]+)}}', re.MULTILINE)


def parse_collection(postman_collection):
    collection = OrderedDict()
    for folder_info in postman_collection['item']:
        group_name = folder_info['name']
        collection[group_name] = parse_group(folder_info['item'])

    return collection


def parse_group(folder_info):
    group = OrderedDict()
    for request_info in folder_info:
        request_name = request_info['name']
        request_name = NAME_SUB_RE.sub('', request_name)
        if 'item' in request_info:
            warnings.warn('Postman sub-folders are not yet supported; '
                          'skipping folder "%s"' % request_name)
            continue
            # for sub_folder in request_info['item']:
            #     group.update(parse_group(sub_folder))
        else:
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
    if body:
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
            warnings.warn('Found unknown body mode "%s"; skipping' % mode)
            return None

        text = yaml.dump(python_repr, indent=4)
        return yaml.YamlLiteralStr(text)

    return None


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('collection', type=open)
    parser.add_argument('--outfile', '-o', type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    postman_collection = json.load(args.collection)
    collection = parse_collection(postman_collection)

    output = yaml.dump(collection, indent=4)
    for var in ENV_SUB_RE.findall(output):
        output = output.replace('{{%s}}' % var,
                                '{{ %s }}' % var.lower())
    print(output, file=args.outfile)


if __name__ == '__main__':
    main()
