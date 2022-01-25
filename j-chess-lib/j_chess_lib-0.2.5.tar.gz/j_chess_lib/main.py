from j_chess_lib.communication import Connection
from j_chess_lib.client import Client


if __name__ == "__main__":

    with Connection("localhost", 5123) as connection1:
        with Connection("localhost", 5123) as connection2:

            from j_chess_lib.ai.Sample import SampleAI

            ai1 = SampleAI()
            ai2 = SampleAI()

            client1 = Client(connection=connection1, ai=ai1)
            client2 = Client(connection=connection2, ai=ai2)

            client1.start()
            print("Client1 started")
            client2.start()
            print("Client2 started")

            client1.join()
            print("Client1 finished")
            client2.join()
            print("Client2 finished")
