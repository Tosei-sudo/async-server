import BaseHTTPServer
import SimpleHTTPServer
# sleep module
import time
import threading

import json
handlersSize = 10

host = 'localhost'

def wait(self):
    time.sleep(1)

class HttpErrorNotFount(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 404

    def __str__(self):
        return self.message

class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def send_response(self, code = 200, data=None, extend={}):
        SimpleHTTPServer.SimpleHTTPRequestHandler.send_response(self, code)
        
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        
        if data:
            self.send_header('Content-Length', str(len(data)))        
        self.send_header('Connection', 'close')
        
        for key in extend.keys():
            self.send_header(key, extend[key])
        
        self.end_headers()
        
        self.wfile.write(data)
        
    def do_GET(self):
        try:
            self.end_headers()
            # send response
            if self.path.startswith('/api/wait'):
                wait(self)
            else:
                pass
            self.send_response(200, "Hello, world!", {'Content-type': 'text/html'})
        except Exception as e:
            
            self.end_headers()
            self.wfile.write(str(e))

class RoadBalance(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        index = self.server.index
        if self.path.startswith('/api'):
            # redirect to sub server
            # # rewrite port number
            to = "http://%s:%d%s" % (host, 8001 + index, self.path)
            self.send_response(302)
            self.send_header('Location', to)
            
            self.end_headers()
            self.wfile.write('Bye')
            self.server.index += 1
            if self.server.index > 10:
                self.server.index = 0
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        index = self.server.index
        datas = {}
        files = {}
            
        if self.path.startswith('/api/upload-file'):
            boundary = self.headers['Content-Type'].split('=')[1]

            formData = self.rfile.read(int(self.headers['Content-Length']))


            parts = formData.split("--" + boundary)
            # print(parts.split('\r\n'))
            for part in parts[1:-1]:
                dataRows = part.split('\r\n')
                
                header = dataRows[1]
                data = dataRows[-2]
                if header.find('filename') != -1:
                    contentType = dataRows[2]
                    if len(dataRows) > 6:
                        data = '\r\n'.join(dataRows[4 : -1])
                    files[header.split(';')[2].split('=')[1].replace('"', '')] = data
                else:
                    datas[header.split(';')[1].split('=')[1].replace('"', '')] = data
            
            for filename in files:
                # print(filename)
                with open('uploads/' + filename, 'wb') as file:
                    file.write(files[filename])
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(datas))
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)

class CustumServer(BaseHTTPServer.HTTPServer):
    index = 0
    
    def __init__(self, server_address, RequestHandlerClass):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)

def start_server():
    try:
        roadbalance_address = (host, 8000)
        roadbalance = CustumServer(roadbalance_address, RoadBalance)
        print('Starting WFS server on port 8000...')
        roadbalance.serve_forever()
        
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        roadbalance.socket.close()

def start_sub_server(i):
    try:
        server_address = (host, 8001 + i)
        httpd = BaseHTTPServer.HTTPServer(server_address, CustomHandler)
        print('Starting Cluster server on port %d...' % (8001 + i) + "\n")
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        httpd.socket.close()

if __name__ == '__main__':
    for i in range(handlersSize + 1):
        thread = threading.Thread(target=start_sub_server, args=(i,))
        thread.start()

    thread = threading.Thread(target=start_server)
    thread.start()
