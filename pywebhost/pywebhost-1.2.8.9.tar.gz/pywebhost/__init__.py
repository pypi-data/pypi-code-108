from http.client import SERVICE_UNAVAILABLE
from pywebhost.modules import BadRequestException
import selectors,socketserver,sys
from socket import socket
from .handler import Request
from .modules import *
# from .modules import *
from re import fullmatch
from http import HTTPStatus

__version__ = '1.2.8.9'

class PathMaker(dict):
    '''For storing and handling path mapping
    
        The keys and values are stored as regex pattern strings
        Keys are used to check is the target URL matching the stored URL,which,using regexes will be a great idea

        To set an item:

            pathmaker['/.*'] = lambda a:SendFile('index.html')

        The server will be finding the functions simply with this:

            pathmaker['/']()

    '''
    def __init__(self):
        super().__init__()

    def __setitem__(self, pattern, value):
        '''Sets an path to be routed'''
        if not isinstance(pattern,str):raise Exception('The keys & values must be regexes string')
        super().__setitem__(pattern,value)

    def hasitem(self,key):
        for pattern in list(self.keys())[::-1]: # LIFO
            if fullmatch(pattern,key):return True

    def __getitem__(self, key):
        '''Iterates all keys to find matching one

        The last one added has a better piority of getting called
        '''
        for pattern in list(self.keys())[::-1]: # LIFO
            if fullmatch(pattern,key):
                return super().__getitem__(pattern)

class PyWebHost(socketserver.ThreadingMixIn, socketserver.TCPServer,):
    '''
        # PyWebHost
        
        To start a server:

            server = PyWebHost(('',1234))
            server.serve_forever()

        You can test by typing `http://localhost:1234` into your browser to retrive a glorious error page ((
    '''    
    request_queue_size = 10
    shutdown_timeout = 5
    def handle_error(self, socket_ : socket, client_address : tuple, error : Exception = ''):
        """Handle an error gracefully. """
        super().handle_error(socket_,client_address)

    def shutdown(self):
        """Stops the serve_forever loop.

        Blocks until the loop has finished or timeout reached.
        . This must be called while serve_forever() is running
         in another thread, or it will deadlock.
        """
        self._BaseServer__shutdown_request = True
        return self._BaseServer__is_shut_down.wait(timeout=self.shutdown_timeout)

    def handle(self, request : Request):
        '''
        Maps the request with the `PathMaker`
        
        The `request` is provided to the router
        '''
        if self.paths.hasitem(request.path):
            try:
                return self.paths[request.path](self,request,None)
                # Succeed,end this handle call
            except BadRequestException as e:
                # For Other server-side exceptions,let the client know
                return request.send_error(e.code,e.explain)
            except ConnectionError as e:
                return request.log_error('Connection Aborted: %s',e)            
            except Exception as e:
                return request.send_error(SERVICE_UNAVAILABLE,explain='There was an error processing your request:%s'%e)
        # Request's not handled:No URI matched
        return request.send_error(HTTPStatus.NOT_FOUND)

    def route(self,pattern):
        '''
        Routes a HTTP Request

        e.g:

            @server.route('/')
            
            def index(server : PyWebHost,request : Request,content):
                request.send_response(200)
        '''
        def wrapper(method):
            self.paths[pattern] = method
            return method
        return wrapper

    def format_error_message(self,code:int,message:str,explain:str,request:Request):
        return f'''
        <head>        
            <title>PyWebHost Error - {self.protocol_version} {code}</title>
        ''' + '''<style>body {font-family: Courier, monospace; } p {position : fixed;bottom:0%;left : 0%;font-size: 14px;}</style>''' + f'''</head><body>
        <div>
            <center><h1>{self.protocol_version} {code} {message}<h1></center><hr>
            <center><h3>{explain}</h3></center>
        </div>
        <p>PyWebHost {__version__}  on {sys.version}</p>
        </body>
        '''

    def __init__(self, server_address : tuple):
        self.daemon_threads = True
        # Handlers terminates with the program
        self.paths = PathMaker()
        # A paths dictionary which has `lambda` objects as keys
        self.protocol_version = "HTTP/1.1"
        # What protocol version to use.        
        # Error page format. %(`code`)d %(`message`)s %(`explain`)s are usable        
        socketserver.TCPServer.allow_reuse_address = True
        # Employ SO_REUSEADDR
        super().__init__(server_address, Request)
