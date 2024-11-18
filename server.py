"""
  @project : http-server
  @author : joy-roy-swe
  @brief 
  @version : 0.1
  @date 2024-11-19
  
  @copyright Copyright (c) 2024

"""
  
import os
import io
import logging
import socket
import http.server
from http import HTTPStatus
from socketserver import TCPServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('http-server')

class ToyTCPServer:
    def __init__(self, socket_address: tuple[str, int], request_handler: 'ToyHTTPRequestHandler') -> None:
        self.request_handler = request_handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(socket_address)
        self.sock.listen()

    def server_forever(self) -> None:
        while True:
            conn, addr = self.sock.accept()

            with conn:
                logger.info(f"Accept connect from {addr}")
                request_stream = conn.makefile('rb')
                response_stream = conn.makefile('wb')
                self.request_handler(
                    request_stream=request_stream,
                    response_stream=response_stream,
                )
            logger.info(f"Closed connection with {addr}")
    
    def __enter__(self) -> 'ToyTCPServer':
        return self
    
    def __exit__(self, *args) -> None:
        self.sock.close()

class ToyHTTPRequestHandler:
    '''
    Serves static files as-is. Only supports GET and HEAD.
    POST returns 403 FORBIDDEN. Other commands return 405 METHOD NOT ALLOWED.

    Supports HTTP/1.1.
    '''
    def __init__(self,
                 request_stream: io.BufferedIOBase,
                 response_stream: io.BufferedIOBase
        ) -> None:
            self.request_stream = request_stream
            self.response_stream = response_stream
            self.command = ''
            self.path = ''
            self.header = {
                'Content-Type': 'text/html',
                'Content-Length': '0',
                'Connection': 'close'
            }
            self.date = ''
            self.handle()
    
    def handle(self) -> None:
        '''Handles the request.'''
        # anything but GET or HEAD will return 405
        # POST will return a 403

        # parse the request to populate
        # self.command, self.path, self.headers

        self._parse_request()

        if not self._validate_path():
            return self._return_404()
        
        if self.command == 'POST':
            return self._return_403()
        
        if self.command not in ('GET', 'HEAD'):
            return self._return_405()
        
        command = getattr(self, f'handle_{self.command}')
        command()
        
