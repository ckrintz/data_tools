from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading, cgi

#test using curl and HTTP via: (USE_HTTPS=False)
#GET: curl http://localhost:8000

#test using curl and HTTP via: (USE_HTTPS=False)
#POST: curl -d name=admin -d shoesize=12 http://localhost:8000

#test using curl and HTTP:  (USE_HTTPS=False)
#put the following 2 lines without the # in a file test.txt
	#hello=world;
	#hey=you
#via POST and a file: 
#curl -d @test.txt http://localhost:8000

#test using curl and https (set USE_HTTPS below to True), use -k to allow self-signed
#generate a self-signed certificate on server side:
#openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
#POST: curl -k -d name=admin -d shoesize=12 https://localhost:8000
USE_HTTPS = False

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello world\t' + threading.currentThread().getName().encode() + b'\t' + str(threading.active_count()).encode() + b'\n')

    def do_POST(self):
        print('post')
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
        self.wfile.write(('Client: %s\n' % str(self.client_address)).encode())
        self.wfile.write(('User-agent: %s\n' % self.headers['user-agent']).encode())
        self.wfile.write(('Path: %s\n' % self.path).encode())
        self.wfile.write(('Form data:\n').encode())

        # Echo back information about what was posted in the form
        print(form.keys())
        for field in form.keys():
            field_item = form[field]
            print(field_item)
            if field_item.filename:
                # The field contains an uploaded file
                print('file')
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write(('\tUploaded %s as "%s" (%d bytes)\n' % \
                        (field, field_item.filename, file_len)).encode())
            else:
                # Regular form value
                value = form[field].value
                self.wfile.write(('\t%s=%s\n' % (field, value)).encode())
                if value == 'on' or value == 'off':
                    myts = time.time()
                    print('{0}:{1}:{2}'.format(myts,field,value))
                    sys.stdout.flush()	
        return


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    server = ThreadingSimpleServer(('0.0.0.0', 8000), Handler)
    if USE_HTTPS:
        import ssl
        server.socket = ssl.wrap_socket(server.socket, keyfile='./key.pem', certfile='./cert.pem', server_side=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")


if __name__ == '__main__':
    run()
