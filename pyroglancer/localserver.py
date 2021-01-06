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

import os
import sys
import tempfile
#from configparser import ConfigParser
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
import types
import shutil


class RequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


class Server(HTTPServer):
    protocol_version = 'HTTP/1.1'

    def __init__(self, server_address):
        HTTPServer.__init__(self, server_address, RequestHandler)


def startserver(address='127.0.0.1', port=8000, directory=tempfile.TemporaryDirectory(), restart=True):

    if restart and 'ngserver' in sys.modules:
        currentserver = sys.modules['ngserver']
        currentdatadir = sys.modules['ngserverdir']
        currsocketaddress = currentserver.socket.getsockname()
        print("Closing server at http://%s:%d" %
              (currsocketaddress[0], currsocketaddress[1]))
        print("Cleaning directory at %s" % (currentdatadir))

        # close previously created server..
        currentserver.server_close()

        # remove only contents inside prev created temp directory
        for filename in os.listdir(currentdatadir):
            filepath = os.path.join(currentdatadir, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)

    args = types.SimpleNamespace()
    args.address = address
    args.port = port
    args.directory = directory

    if isinstance(args.directory, tempfile.TemporaryDirectory):
        temp_dir = args.directory
        temp_dirname = temp_dir.name
    else:
        temp_dirname = args.directory

    os.chdir(temp_dirname)
    print("Serving data from: ", temp_dirname)
    server = Server((args.address, args.port))
    socketaddress = server.socket.getsockname()
    print("Serving directory at http://%s:%d" %
          (socketaddress[0], socketaddress[1]))

    sys.modules['ngserver'] = server
    sys.modules['ngserverdir'] = str(os.getcwd())

    # # save config information..
    # config = ConfigParser(strict=False)
    # config_dir = os.path.join(os.path.expanduser("~"), '.config/pyroglancer')
    # if not os.path.exists(config_dir):
    #     os.makedirs(config_dir)
    #
    # config_file = os.path.join(config_dir, 'pyroglancer.ini')
    # config.read(config_file)
    # if not config.has_section('localserver'):
    #     config.add_section('localserver')
    # config.set('localserver', 'directory', str(os.getcwd()))
    # config.set('localserver', 'port', str(socketaddress[1]))
    #
    # with open(config_file, 'w') as f:
    #     config.write(f)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Serving now..')
    finally:
        server.server_close()
        if isinstance(args.directory, tempfile.TemporaryDirectory):
            temp_dir.cleanup()
        sys.exit(0)


def startdataserver():

    serverthread = Thread(target=startserver)
    serverthread.daemon = True  # This thread dies when main thread (only non-daemon thread) exits..
    serverthread.start()
