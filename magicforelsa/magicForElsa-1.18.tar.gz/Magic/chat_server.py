# see https://www.youtube.com/watch?v=3UOyky9sEQY for a BASIC IDEA of how this works
import json
import os.path
import socket
import threading

host, port, clients, nicknames = "127.0.0.1", 24094, [], []
# SOCK_STREAM. AF_INET refers to the address-family ipv4. The SOCK_STREAM means connection-oriented TCP protocol.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
try: os.makedirs("serverdata")  # Make the directory to store the syncing data
except: pass


def jsonenc(rec, data) -> str:
    """To convert the json data"""
    return json.dumps({"rec": rec, "data": data})


def jsondec(data: str) -> dict:
    """To convert the json data"""
    return json.loads(data)


def broadcast(username: str, message: str) -> None:
    """To send the message to a specific client"""
    try:
        message = str(message)
        print("Client found: ", client := clients[nicknames.index(username)], 'Msg send: ', message)
        client.send(jsonenc("msg", message).encode("ascii"))
    except Exception as e: print(e, "No user found")


def handle(client: object) -> None:
    """Recieve data from a client"""
    while True:
        try:
            raw_message = client.recv(1024).decode("ascii")
            header = jsondec(raw_message)["rec"]
            match header:
                case "msg":
                    username, message = jsondec(raw_message)["data"][0], jsondec(raw_message)["data"][1]
                    print(raw_message)
                    print(jsondec(raw_message)["data"])
                    print(f"{username} : {message}")
                    print("Broadcasting message to ", username)
                    broadcast(username, message)
                case "fsync":
                    nicname, jsonstr = jsondec(raw_message)["data"][0], jsondec(raw_message)["data"][1]
                    with open('./serverdata/' + nicname + '.json', 'w') as f:
                        f.write(jsonstr)
                    print(nicname, 'data synced')
                case "sync":
                    nicname = jsondec(raw_message)["data"]
                    try:
                        dat = json.loads(open('./serverdata/' + nicname + '.json', 'r').read())
                        client.send(jsonenc("sync", dat).encode("ascii"))
                        print("Has send the data to", nicname)

                    except Exception as e: print(e, 'File not found' + nicname)




        except Exception as e:
            print(e, client, "not Functioning properly")
            # if error happens, remove the client
            # get the index to remove it from the nickname
            # the index for the client and nickname will be the same
            nicknames.pop(clients.index(client))  # Removing from nickname by getting the index of client
            clients.remove(client)
            client.close()
            del client
            break


def recieve() -> None:
    """To connect the client with the server"""
    while True:
        try:
            client, address = server.accept()
            print(f"connected with address: {address}")
            client.send(jsonenc("Nick", '').encode("ascii"))
            nickname = client.recv(1024).decode("ascii")
            nicknames.append(nickname := (jsondec(nickname)["data"]))
            clients.append(client)
            print(f"{nickname} {address}")
            threading.Thread(target = handle, args = (client,)).start()
        except Exception as e:
            print(e)


def startserver() -> None:
    """To chat the start server"""
    print("Server has started")
    recieve()


if __name__ == '__main__': startserver()
