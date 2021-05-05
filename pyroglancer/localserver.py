#    This script is part of pyroglancer (https://github.com/SridharJagannathan/pyroglancer).
#    This code was adapted using the cors_webserver module present in the neuroglancer package
#    for serving data from a local directory via http port.
#    The implementation for the range requests was adapted from RangeHTTPServer module.

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
import re
import sys
import tempfile
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
import types
import shutil


def copy_byte_range(infile, outfile, start=None, stop=None, bufsize=16*1024):
    '''Like shutil.copyfileobj, but only copy a range of the streams.
    Both start and stop are inclusive.
    '''
    if start is not None:
        infile.seek(start)
    while 1:
        to_read = min(bufsize, stop + 1 - infile.tell() if stop else bufsize)
        buf = infile.read(to_read)
        if not buf:
            break
        outfile.write(buf)


BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')


def parse_byte_range(byte_range):
    '''Returns the two numbers in 'bytes=123-456' or throws ValueError.
    The last number or both numbers may be None.
    '''
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range %s' % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError('Invalid byte range %s' % byte_range)
    return first, last


class RequestHandler(SimpleHTTPRequestHandler):
    """This class provides support for generic cors access, HTTP 'Range' requests
    In case of the range implementation, the approach is to:
    - Override send_head to look for 'Range' and respond appropriately.
    - Override copyfile to only transmit a range when requested.
    """

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.send_head()

    def send_head(self):
        if 'Range' not in self.headers:
            self.range = None
            return SimpleHTTPRequestHandler.send_head(self)
        try:
            self.range = parse_byte_range(self.headers['Range'])
        except ValueError as e:
            err_string = 'Invalid byte range with: ' + e
            self.send_error(400, err_string)
            return None
        first, last = self.range

        # Mirroring SimpleHTTPServer.py here
        path = self.translate_path(self.path)
        f = None
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, 'File not found')
            return None

        fs = os.fstat(f.fileno())
        file_len = fs[6]
        if first >= file_len:
            self.send_error(416, 'Requested Range Not Satisfiable')
            return None

        self.send_response(206)
        self.send_header('Content-type', ctype)
        self.send_header('Accept-Ranges', 'bytes')

        if last is None or last >= file_len:
            last = file_len - 1
        response_length = last - first + 1

        self.send_header('Content-Range',
                         'bytes %s-%s/%s' % (first, last, file_len))
        self.send_header('Content-Length', str(response_length))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def end_headers(self):
        """Allow responses to be shared with any requester without any credentials."""
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def copyfile(self, source, outputfile):
        if not self.range:
            return SimpleHTTPRequestHandler.copyfile(self, source, outputfile)

        # SimpleHTTPRequestHandler uses shutil.copyfileobj, which doesn't let
        # you stop the copying before the end of the file.
        start, stop = self.range  # set in send_head()
        copy_byte_range(source, outputfile, start, stop)


class Server(HTTPServer):
    """Class for basic HTTP server."""

    protocol_version = 'HTTP/1.1'

    def __init__(self, server_address):
        """Initialise HTTP server."""
        HTTPServer.__init__(self, server_address, RequestHandler)


def closedataserver(removefiles=True):
    """Close a already started dataserver.

    Parameters
    ----------
    removefiles :  flag to remove the created contents in the hosted server

    Returns
    -------
    None
    """
    if (('ngserver' in sys.modules) and ('ngserverdir' in sys.modules)):
        currentserver = sys.modules['ngserver']
        currentdatadir = sys.modules['ngserverdir']
        currsocketaddress = currentserver.socket.getsockname()
        print("Closing server at http://%s:%d" %
              (currsocketaddress[0], currsocketaddress[1]))

        # close previously created server..
        currentserver.server_close()

        del sys.modules['ngserver']
        del sys.modules['ngserverdir']

        # close previously created ng viewer..
        if ('ngviewerinst' in sys.modules):
            del sys.modules['ngviewerinst']

        if removefiles:
            print("Cleaning directory at %s" % (currentdatadir))
            # remove only contents inside prev created temp directory
            for filename in os.listdir(currentdatadir):
                filepath = os.path.join(currentdatadir, filename)
                try:
                    shutil.rmtree(filepath)
                except OSError:
                    os.remove(filepath)
        else:
            print("Directory is not cleaned at %s" % (currentdatadir))


def _startserver(address='127.0.0.1', port=8000, directory=tempfile.TemporaryDirectory(), restart=True):
    """Start a dataserver that can host local folder via http.

    Parameters
    ----------
    address :  ip address to use for the local host server
    port :     port number to use for the local host server
    directory :   local directory to be used for hosting
    restart :   restart/clean up already running data server

    Returns
    -------
    None
    """
    if restart and 'ngserver' in sys.modules:
        closedataserver()

    args = types.SimpleNamespace()
    args.address = address
    args.port = port
    args.directory = directory

    if args.directory is None:
        args.directory = tempfile.TemporaryDirectory()

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

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Serving now..')
    finally:
        server.server_close()
        if isinstance(args.directory, tempfile.TemporaryDirectory):
            temp_dir.cleanup()
        sys.exit(0)


def startdataserver(address='127.0.0.1', port=8000, directory=None,
                    restart=True):
    """Start a dataserver thread(return control back) that can host local folder via http.

    Parameters
    ----------
    address :  str
        ip address to use for the local host server
    port :  int
        port number to use for the local host server
    directory :  str
        local directory to be used for hosting
    restart :  bool
        restart/clean up already running data server
    """
    serverthread = Thread(target=_startserver, args=(address, port, directory, restart))
    serverthread.daemon = True  # This thread dies when main thread (only non-daemon thread) exits..
    serverthread.start()
