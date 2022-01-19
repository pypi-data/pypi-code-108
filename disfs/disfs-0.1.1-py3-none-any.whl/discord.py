from .utils import convert_to_png, decode_int, encode_int, pbget, pbmpost
from requests import Session, get
from time import time, sleep
from json import dumps

class Discord:
    overhead = 137
    api_url = "https://discord.com/api/v8"
    
    def api_request(self, method, path, data={}, query={}, json={}, file=None):
        if self.timeout > 0:
            sleep(self.timeout + 0.1)
        
        if file:
            resp = pbmpost(method, self.api_url + path, convert_to_png(file), self.session, extra_data=data, filename="upload.png")
        else:
            if method != "GET":
                resp = self.session.request(method, self.api_url + path, params=query, json=json)
            else:
                resp = self.session.request(method, self.api_url + path, params=query)
        
        if resp.headers.get("x-ratelimit-remaining", "1") == "0":
            timeout = float(resp.headers.get("x-ratelimit-reset-after", "-1"))
            
            if timeout == -1:
                timeout = float(resp.headers["x-ratelimit-reset"]) - time()
            
            self.timeout = timeout
        
        try:
            json = resp.json()
        except:
            json = {}
        
        if "retry_after" in json:
            self.timeout = json["retry_after"]
        
        resp.raise_for_status()
        return json
    
    def login(self, token, channel, listing):
        self.token = token
        self.channel = channel
        self.listing = listing
        self.timeout = 0.0
        self.session = Session()
        
        self.session.headers.update({"Authorization": f"Bot {self.token}"})
        self.api_request("GET", f"/channels/{self.channel}")
        self.api_request("GET", f"/channels/{self.listing}")
    
    def upload(self, data):
        return self.api_request("POST", f"/channels/{self.channel}/messages", data={"payload_json": '{"content": "", "tts": false}'}, file=data)["id"]
    
    def delete(self, chunk_id, listing=False):
        channel = [self.channel, self.listing][listing]
        self.api_request("DELETE", f"/channels/{channel}/messages/{chunk_id}")
    
    def download(self, chunk_id, header_only=False, progress=True):
        url = self.api_request("GET", f"/channels/{self.channel}/messages/{chunk_id}")["attachments"][0]["url"]
        
        if header_only:
            stream = get(url, stream=True).raw
            header_len = decode_int(stream.read(self.overhead + 4)[self.overhead:])
            return encode_int(header_len) + stream.read(header_len)
        else:
            return pbget(url, disable=not progress)[self.overhead:]
    
    def get_listing(self):
        page = self.api_request("GET", f"/channels/{self.listing}/messages", query={"limit": "100"})
        listing = []
        
        while page != []:
            listing += page
            page = self.api_request("GET", f"/channels/{self.listing}/messages", query={"limit": "100", "after": page[0]["id"]})
        
        return listing
    
    def add_entry(self, entry):
        return self.api_request("POST", f"/channels/{self.listing}/messages", json={"content": entry, "tts": False})["id"]
