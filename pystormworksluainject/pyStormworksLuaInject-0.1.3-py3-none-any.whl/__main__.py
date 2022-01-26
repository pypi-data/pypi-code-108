import os, sys, re, time, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from html import escape

done = False

def main():
    global code
    global done

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, a, b, c, d):
            pass
        def do_GET(self):
            global done
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(outfile[:outfile.rindex('.')].encode('utf-8'))
            done = True
            s.stop()

    class Server(threading.Thread):
        def run(self):
            self.server = ThreadingHTTPServer(('127.0.0.1', 15735), Handler)
            self.server.serve_forever()
        def stop(self):
            self.server.shutdown()
            
    def repl(foo):
        return foo[0][:foo.span(1)[0]-foo.span(0)[1]] + escape(code) + foo[0][foo.span(1)[1] - foo.span(0)[0]:]

    #print("\n------\nPython's Turn!\n------\n")
    outfile = sys.argv[1]
    root_path = os.getenv('APPDATA')+"/Stormworks/data/vehicles/"
    data = open(root_path+outfile).read()

    for file in os.scandir(sys.argv[2]):
        code = open(file.path).read()
        identifier = file.name[:file.name.rindex('.')]
        print(f"Searching '{outfile}' for Lua blocks with identifier '{identifier}'")
        data, c = re.subn(f"script=['\"]--{identifier}[\r\n|\n|\r](.*?)['\"]>", repl, data, flags = re.MULTILINE + re.DOTALL)
        open(root_path+outfile, "w").write(data)
        print(f"\tReplaced {c} Lua blocks with identifier '{identifier}'.")
    #print("\n------\nBack to you, nameous!\n------\n")

    s = Server()
    s.start()

    for i in range(10):
        time.sleep(1)
        print(f"{10-i} .. ", end="")
        if done:
            print("File served")
            break
    if not done:
        print("Timeout")
    s.stop()

if __name__ == "__main__":
    main()