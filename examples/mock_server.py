#!/usr/bin/env python3
"""Run this file to create a mock server.

This is provided as a way to run restcli with the example workspaces and get
somewhat realistic behavior.
"""

import http.server
import json
import urllib.parse
from http import HTTPStatus
from typing import NamedTuple, Optional, Tuple


class Resource(NamedTuple):
    model: str
    id: Optional[str]
    data: dict


OBJECTS = {}


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        resource = self.get_resource()
        if not resource:
            return

        self.write_json_body(resource.data)

    def do_POST(self):
        resource = self.get_resource(detail=False)
        if not resource:
            return

        data = self.read_json_body()
        if not data:
            return

        id_ = data.get("id")
        if not id_:
            return self.error_response(
                HTTPStatus.BAD_REQUEST, "Field 'id' is required."
            )

        OBJECTS[resource.model][id_] = data
        self.write_json_body(data, status_code=HTTPStatus.CREATED)

    def do_PATCH(self):
        resource = self.get_resource(detail=True)
        if not resource:
            return

        data = self.read_json_body()
        if not data:
            return

        obj = OBJECTS[resource.model][resource.id]
        for key, value in data.items():
            if key in obj and key != "id":
                obj[key] = value

        self.write_json_body(obj)

    def do_PUT(self):
        resource = self.get_resource(detail=True)
        if not resource:
            return

        data = self.read_json_body()
        if not data:
            return

        obj = OBJECTS[resource.model][resource.id]
        for key in obj:
            if key not in data:
                return self.error_response(
                    HTTPStatus.BAD_REQUEST, f"Field '{key}' is missing'"
                )
            if key != "id":
                obj[key] = data[key]

        self.write_json_body(obj)

    def do_DELETE(self):
        resource = self.get_resource(detail=True)
        if not resource:
            return

        del OBJECTS[resource.model][resource.id]
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def get_resource(self, detail=None) -> Optional[Resource]:
        path = urllib.parse.urlparse(self.path).path.strip("/")
        parts = path.split("/")
        if len(parts) == 0 or not any(parts):
            return self.error_response(HTTPStatus.NOT_FOUND)

        model = parts[0]
        try:
            data = OBJECTS[model]
        except KeyError:
            data = OBJECTS[model] = {}

        if len(parts) > 1 and parts[1]:
            id_ = parts[1]
            if detail is False:
                return self.error_response(
                    HTTPStatus.BAD_REQUEST, f"Unexpected resource id in path.",
                )

            try:
                data = data[id_]
            except KeyError:
                return self.error_response(HTTPStatus.NOT_FOUND)
        else:
            if detail is True:
                return self.error_response(
                    HTTPStatus.BAD_REQUEST, "Missing resource id in path."
                )

            id_ = None

        return Resource(model, id_, data)

    def read_json_body(self):
        if not self.headers["Content-Length"]:
            return self.error_response(
                HTTPStatus.BAD_REQUEST, "Header 'Content-Length' is required."
            )

        content_length = int(self.headers["Content-Length"])
        req_body = self.rfile.read(content_length)

        return json.loads(req_body.decode("utf-8"))

    def write_json_body(self, body: dict, status_code=HTTPStatus.OK):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        res_body = json.dumps(body).encode("utf-8")
        self.wfile.write(res_body)

    def error_response(self, code: HTTPStatus, msg: Optional[str] = None):
        self.send_response(code)
        if msg:
            self.send_header("Content-Type", "application/json")
        self.end_headers()
        if msg:
            self.write_json_body({"detail": msg})


if __name__ == "__main__":
    server = http.server.HTTPServer(("localhost", 8000), RequestHandler)
    print("Server started at localhost:8000. Press <Ctrl+C> to quit.")
    server.serve_forever()
