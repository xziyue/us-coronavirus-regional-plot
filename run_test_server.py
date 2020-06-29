from http.server import HTTPServer, SimpleHTTPRequestHandler

server = HTTPServer(('127.0.0.1', 12345), SimpleHTTPRequestHandler)
server.serve_forever()