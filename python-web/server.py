from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os, sys, cgi, time
import urllib.parse
#https://pymotw.com/2/BaseHTTPServer/index.html#module-BaseHTTPServer
class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    
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
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write('\tUploaded %s as "%s" (%d bytes)\n' % \
                        (field, field_item.filename, file_len))
            else:
                # Regular form value
                value = form[field].value
                self.wfile.write('\t%s=%s\n' % (field, value))
                if value == 'on' or value == 'off':
                    myts = time.time()
                    print('{0}:{1}:{2}'.format(myts,field,value))
                    sys.stdout.flush()	
        return

    def do_GET(self):
        print('get')
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return


if __name__ == '__main__':

    IP = 'localhost'
    PORT = 8000 
    if len(sys.argv) > 2:
        PORT = int(sys.argv[2])
        IP = sys.argv[1]
    elif len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    CWD = os.getcwd()
    server = ThreadingSimpleServer((IP, PORT), SimpleHTTPRequestHandler)
    print("Serving HTTP traffic from", CWD, "on", IP, "using port", PORT)
    try:
        while 1:
            sys.stdout.flush()
            server.handle_request()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")
