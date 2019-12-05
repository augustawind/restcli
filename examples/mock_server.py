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

    def write_json_body(self, body: dict):
        res_body = json.dumps(body).encode("utf-8")
        self.wfile.write(res_body)

    def error_response(self, code: HTTPStatus, msg: Optional[str] = None):
        self.send_response(code)
        if msg:
            self.send_header("Content-Type", "application/json")
        self.end_headers()
        if msg:
            self.write_json_body({"detail": msg})

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

    def do_GET(self):
        resource = self.get_resource()
        if not resource:
            return

        self.send_response(HTTPStatus.CREATED)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.write_json_body(resource.data)

    def do_DELETE(self):
        resource = self.get_resource(detail=True)
        if not resource:
            return

        del OBJECTS[resource.model][resource.id]
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_POST(self):
        if not self.headers["Content-Length"]:
            return self.error_response(
                HTTPStatus.BAD_REQUEST, "Header 'Content-Length' is required."
            )

        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)

        obj = json.loads(body.decode("utf-8"))
        id_ = obj.get("id")
        if not id_:
            return self.error_response(
                HTTPStatus.BAD_REQUEST, "Field 'id' is required."
            )

        resource = self.get_resource(detail=False)
        if not resource:
            return

        OBJECTS[resource.model][id_] = obj
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.write_json_body(obj)


if __name__ == "__main__":
    server = http.server.HTTPServer(("localhost", 8000), RequestHandler)
    print("Server started at localhost:8000. Press <Ctrl+C> to quit.")
    server.serve_forever()
