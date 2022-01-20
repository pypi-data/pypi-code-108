import paho.mqtt.client as mqtt
import ssl
import time
import json
import requests
import uuid
import hashlib


class Client(object):

    def __init__(self, API_KEY=None, USER_ID=None, GROUP_ID=None, CALLBACK=None):

        # Check for API_KEY
        if not API_KEY:
            print("Please provide a valid API KEY to proceed")
            exit()

        # Fetch account_id and project_id for channel structure
        self.account_id, self.project_id = self.fetch_details(API_KEY)

        SALT="x9nFgM1ioxAOPmT3Fdyeh483lerc1J7k"
        
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(["mqtt"])
        client_id, username, password = self.gen_user_client_pass(
            API_KEY, SALT)

        self.callback_function = CALLBACK

        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        self.channel_name = f"locations/{self.account_id}/{self.project_id}/+"
        self.user_id = None

        self.client.on_message = self.on_message

        if GROUP_ID:
            USER_ID = self.get_users_from_group(API_KEY, GROUP_ID)
            if not USER_ID:
                print("Please add some users to receive locations.")
                exit()

        if USER_ID is None:
            self.client.on_connect = self.on_connect
        else:
            self.user_id = USER_ID
            self.client.on_connect = self.on_connect_user_id

        self.client.tls_set_context(context=ctx)
        self.client.username_pw_set(
            username+"?x-amz-customauthorizer-name=iot-authorizer", password)
        self.client.connect(
            "az91jf6dri5ey-ats.iot.eu-central-1.amazonaws.com", port=443)

        print("Successfully Initialised")

    def fetch_details(self, api_key):
        url = "https://sdk.geospark.co/api/details"
        payload = {}
        headers = {'api-key': api_key}
        response = requests.request("GET", url, headers=headers, data=payload)
        response = json.loads(response.text).get("data")
        return response.get("account_id"), response.get("project_id")

    def gen_user_client_pass(self, API_KEY, SALT):
        timestamp = str(time.time())
        client_id = API_KEY + "_" + str(uuid.uuid4())
        username = "api_"+timestamp
        password = hashlib.sha512(
            (API_KEY+timestamp+SALT).encode()).hexdigest()
        return client_id, username, password

    def get_users_from_group(self, api_key, group_id):
        url = "https://sdk.geospark.co/api/group/" + group_id
        payload = {}
        headers = {'api-key': api_key}
        response = requests.request("GET", url, headers=headers, data=payload)
        response = json.loads(response.text).get("data")
        return response.get("user_ids")

    def on_message(self, client, userdata, msg):
        json_data = json.loads(msg.payload)
        if not self.callback_function:
            print("Location Data: ", json_data)
        else:
            print("Passing to callback function.")
            self.callback_function(json_data)
        
    def on_connect(self, client, userdata, flags, rc):
        print("Connected successfully")
        client.subscribe(self.channel_name)

    def on_connect_user_id(self, client, userdata, flags, rc):
        print("Connected successfully")
        if isinstance(self.user_id, list):
            for user in self.user_id:
                self.channel_name = self.channel_name[:-1] + user
                client.subscribe(self.channel_name)
        else:
            self.channel_name = self.channel_name[:-1] + self.user_id
            client.subscribe(self.channel_name)

    def disconnect(self):
        self.client.unsubscribe("*")
        self.client.disconnect()
        print("Disconnected successfully.")

    def sub(self):
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.disconnect()
