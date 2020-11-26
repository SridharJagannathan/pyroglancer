#    This script is part of pyroglancer (https://github.com/SridharJagannathan/pyroglancer).
#    This code was adapted using the cors_webserver module present in the neuroglancer package
#    for serving data from a local directory via http port.

#    Copyright (C) 2020 Sridhar Jagannathan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

# TODO:
# - Add support for server to look at gzip files using do_GET()

"""This code is used to serve local data via http port, so it can be read by neuroglancer."""

import argparse
import os
import sys
import tempfile

from http.server import SimpleHTTPRequestHandler, HTTPServer


class RequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


class Server(HTTPServer):
    protocol_version = 'HTTP/1.1'

    def __init__(self, server_address):
        HTTPServer.__init__(self, server_address, RequestHandler)


def startserver(args):
    if isinstance(args.directory, tempfile.TemporaryDirectory):
        temp_dir = args.directory
        temp_dirname = temp_dir.name
    else:
        temp_dirname = args.directory
    os.chdir(temp_dirname)
    server = Server((args.address, args.port))
    socketaddress = server.socket.getsockname()
    print("Serving directory %s at http://%s:%d" %
          (os.getcwd(), socketaddress[0], socketaddress[1]))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        if isinstance(args.directory, tempfile.TemporaryDirectory):
            temp_dir.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--address', default='127.0.0.1', help='IP address')
    ap.add_argument('-p', '--port', type=int, default=8000, help='Port to serve data on')
    ap.add_argument('-d', '--directory', default=tempfile.TemporaryDirectory(),
                    help='Directory to serve the data from')

    args = ap.parse_args()

    startserver(args)
