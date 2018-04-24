from  http.server import *
import socketserver
from urllib.parse import urlparse, parse_qs

class RequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		print(self.requestline)
		print(self.headers)
		print(self.address_string())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
	try:
	    server_address = ('', port)
	    httpd = server_class(server_address, handler_class)
	    httpd.serve_forever()
	except Exception as exc:
		print('run http server error : {}'.format(exc))    

if __name__ == '__main__':
	run()    