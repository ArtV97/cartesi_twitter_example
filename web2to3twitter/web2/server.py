import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import twitter_db as db

db_conn = None

HOST = "0.0.0.0"
PORT = 8080

files_map = {}

def build_files_map():
    for filename in os.listdir():
        if filename[0] == '.' or filename[:2] == "__" or os.path.isdir(filename):
            continue
        
        extension = filename[filename.rfind("."):]
        content_type = None
        charset = None
        
        if extension == ".html":
            content_type = "text/html"
            charset = "utf-8"
        elif extension == ".js":
            content_type = "application/javascript" # "text/javascript"
            charset = "utf-8"
        elif extension == ".png":
            content_type = "image/png"
        else:
            continue # ignore python files and "unknown" files

        if charset:
            content_type += f";charset={charset}"
        
        path = "/"
        if filename != "index.html":
            path += filename
        
        files_map[path] = {
                        "filename": filename,
                        "content_type": content_type
                    }


class MyServer(BaseHTTPRequestHandler):
    # serves html page
    def do_GET(self):
        if self.path in files_map:
            file_info = files_map[self.path]

            self.send_response(200)
            self.send_header("Content-type", file_info["content_type"])
            self.end_headers()

            with open(file_info["filename"], "rb") as f:
                content = f.read()
                self.wfile.write(content)
        else:
            self.send_error(404)

    # process data request
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_len)
        body.decode("utf-8")

        # [["db_function0", arg0, arg1], ["db_function1", arg0], ...]
        body_json = None
        try:
            body_json = json.loads(body)
        except json.decoder.JSONDecodeError:
            self.send_error(500, "Invalid JSON received.")
        
        if type(body_json) != list:
            self.send_error(500, "Expect list.")

        result = []
        for item in body_json:
            f_name = item[0]
            args = [db_conn]

            if len(item) > 1:
                args += item[1:]
            
            print(f_name, args)
            func = getattr(db, f_name) # get function ref
            print(func)

            try:
                result.append({"success": True, "result": func(*args)})
            except Exception as e:
                result.append({"success": False, "result": str(e)})

        self.send_response(200) # 200 = ok
        self.send_header("Content-type", "application/json; charset=UTF-8")
        self.end_headers()
        response = json.JSONEncoder().encode(result)
        response_bytes = response.encode("utf-8")
        self.wfile.write(response_bytes)



if __name__ == "__main__":
    build_files_map()
    
    db_conn = db.create_connection()

    webServer = HTTPServer((HOST, PORT), MyServer)
    print("Server started at http://{}:{}".format(HOST, PORT))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    db_conn.close()

    webServer.server_close()
    print("Server stopped.")