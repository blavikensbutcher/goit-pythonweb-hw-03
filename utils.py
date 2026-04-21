from http.server import BaseHTTPRequestHandler
import urllib.parse
import os
import mimetypes
import json

from helpers import write_json, render_template


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('templates/index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('templates/message.html')
        elif pr_url.path == '/read':
            self.send_read_page()
        elif pr_url.path == '/style.css':
            self.send_static_file('static/style.css')
        elif pr_url.path.startswith('/static/'):
            filepath = pr_url.path[1:] 
            self.send_static_file(filepath)
        else:
            self.send_html_file('templates/error.html', 404)
            
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = dict(el.split("=") for el in data_parse.split("&"))

        write_json(data_dict)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static_file(self, filename, status=200):
        if os.path.exists(filename):
            self.send_response(status)
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type:
                self.send_header('Content-type', mime_type)
            self.end_headers()
            with open(filename, 'rb') as fd:
                self.wfile.write(fd.read())
        else:
            self.send_html_file('templates/error.html', 404)

    def send_read_page(self):
        messages = {}
        data_file = 'storage/data.json'
        
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            except json.JSONDecodeError:
                messages = {}
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = render_template('read.html', messages=messages)
        self.wfile.write(html)



