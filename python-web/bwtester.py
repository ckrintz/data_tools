from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading, cgi

#install dependencies
#pip3 install pyopenssl httpserver

#run via
#python3 bwtester.py

#test using curl and HTTP via: 
#GET: curl http://IP:PORT
#POST: curl -d @test.jpg http://IP:PORT
	#response is
	#size: $fsize elapsed time:  $elapsed_time, bw: $bandwidth

PORT = 8282
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'GET: No file transferred\n')

    def do_POST(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        self.end_headers()

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                self.wfile.write(b'POST: file transferred\n')
            else:
                self.wfile.write(b'POST: no file transferred\n')
        return


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    print("Threaded server is listening on port {}...".format(PORT))
    server = ThreadingSimpleServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")


if __name__ == '__main__':
    run()
