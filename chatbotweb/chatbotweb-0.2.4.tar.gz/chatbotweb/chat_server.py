from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib import parse as urlparse

class ChatServer():

    def __init__(self,chat_class, user_class):
        self.access_list = {}
        self.chat_obj = chat_class()
        self.user_class = user_class

    def handler(self, *args):
        ip_address = args[1][0]
        user_obj = None
        if ip_address in self.access_list:
            user_obj = self.access_list[ip_address]
        else:
            user_obj = self.user_class(self.chat_obj)
            user_obj.ip_address = ip_address
            self.access_list[ip_address] = user_obj

        return ChatRequestHandler(self.chat_obj,user_obj,*args)

    def start(self, address, port):
        server = HTTPServer((address, int(port)), self.handler)
        print("server start")
        print("access : http://localhost:"+str(port))
        print("please press ctrl+c if you want to stop server")
        server.serve_forever()

class ChatRequestHandler(BaseHTTPRequestHandler):

    def __init__(self,chat_obj ,user_obj, *args):
        self.user_obj = user_obj
        self.chat_obj = chat_obj
        BaseHTTPRequestHandler.__init__(self, *args)

    def api_say(self):
        content_len  = int(self.headers.get("content-length"))
        contents = self.rfile.read(content_len).decode("utf-8")
        response_dict = dict(urlparse.parse_qsl(contents))
        self.send_response(200)
        self.end_headers()

        txt = ""
        if "txt" in response_dict:
            txt = response_dict["txt"]

        self.user_obj.response_param = response_dict

        message, continuous_flag = self.user_obj.callback_method(txt)
        if message != None:
            if type(message) == list:
                for s in message:
                    self.wfile.write(s.encode())
            elif type(message) == str:
                self.wfile.write(message.encode())

        if continuous_flag == False:
            message = "。#finish"
            self.wfile.write(message.encode())
        return

    default_view = """
        <style>
            h1   { background-color: #ffe0e0; }
            div  { padding:10px; }
            span { border-radius: 10px; background-color: #ffe0e0; padding:8px; }
            .bot { text-align: left; }
            .usr { text-align: right; }
        </style>
        <h1>チャットボットと会話しよう</h1>
    """

    main_view = """
        <html><meta charset="utf-8"><body>
        <script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
        <userdef>
        <div id="chat"><init_chat_html></div>
        <div class='usr'><input id="txt" size="40">
        <button id="button" onclick="robotSay()">発言</button></div>
        <script>
        
        var url = ".";
        function htmlentities(str){
          return String(str).replace(/&/g, "&amp;")
            .replace(/"/g, "&quot;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        }

        function robotSay() {
            
            $("#txt").prop('disabled', true);
            $("#button").prop('disabled', true);

            var txt = $('#txt').val();
            if(esc(txt) != ""){
                var user_html = "<div class='usr'><span>" + esc(txt) + "</span>:あなた</div>";
                $('#chat').html($('#chat').html() + user_html);
            }

            $('#txt').val('').focus();
            
            $.post(url, {"txt":htmlentities(txt)},
                function(res) {
                    (async () => {
                        const sleep = (second) => new Promise(resolve => setTimeout(resolve, second * 1000))
                        var textArr = esc(res).split("。");
                        for (var i = 0, len = textArr.length; i < len; ++i) {
                            if(!textArr[i].startsWith("#") & textArr[i] != ""){
                                <time_delay>
                                var robot_html = "<div class='bot'><bot_name>:<span>" + textArr[i] + "</span></div>";
                                $('#chat').html($('#chat').html() + robot_html);
                            }
                        }
                        if($.inArray("#finish",textArr)==-1){
                            $("#txt").prop('disabled', false);
                            $("#button").prop('disabled', false);                  
                        }
                    })()
                });
        }
        function esc(s) {
            return s.replace('&', '&amp;').replace('<','&lt;')
                    .replace('>', '&gt;');
        }

        </script></body></html>
        """

    error_view = """
        <html><meta charset="utf-8"><body>
        <script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
        エラーが発生しました <error-log>
        </body></html>
        """

    def show_form(self, query_dic):
        self.send_response(200)
        self.end_headers()

        message = None

        try:
            startup_utterance = self.user_obj.init_function(query_dic)
            message = ChatRequestHandler.main_view.replace("<bot_name>",self.chat_obj.BOT_NAME)
            
            if startup_utterance is not None:
                textArr = startup_utterance.split("。")
                context_init_robot = ""
                for t in textArr:
                    if t != '':
                        context_init_robot += """<div class="bot">""" + self.chat_obj.BOT_NAME + """:<span>""" + t + """</span></div>"""
                # message = message.replace("<init_chat_html>","""<div class="bot">""" + self.chat_obj.BOT_NAME + """:<span>""" + startup_utterance + """</span></div>""")
                message = message.replace("<init_chat_html>",context_init_robot)
            else:
                message = message.replace("<init_chat_html>","")
            
            if hasattr(self.chat_obj,"html") and self.chat_obj.html is not None:
                message = message.replace("<userdef>",self.chat_obj.html)
            else:
                message = message.replace("<userdef>",ChatRequestHandler.default_view)

            if hasattr(self.user_obj,"valid_deray") and self.user_obj.valid_deray:
                message = message.replace("<time_delay>","await sleep(3);") 
            else:
                message = message.replace("<time_delay>","") 


        except Exception as e:
            message = ChatRequestHandler.error_view
            message = message.replace("<error-log>",str(e))

        self.wfile.write(message.encode())
        return

    def do_GET(self):
        parse_result = urlparse.urlparse(self.path)
        if parse_result.path == "/":
            query_dic = urlparse.parse_qs(parse_result.query)
            self.show_form(query_dic)

    def do_POST(self):
        self.api_say()