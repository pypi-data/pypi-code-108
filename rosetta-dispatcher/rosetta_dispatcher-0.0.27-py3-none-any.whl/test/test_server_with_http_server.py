import os
from time import sleep

from rosetta_dispatcher.dispatch_server import DispatchServer
from rosetta_dispatcher.model.dispatch_response_model import DispatchResponseModel
from rosetta_dispatcher.model.dispatch_types import DispatchResponseStatus

def dispatch_server():
    host = '61.160.36.168'
    port = 4032

    ds = DispatchServer(redis_host=host, redis_port=port)

    count = 0
    while True:
        print('hello world!!!')
        result = ds.fetch('NMT_RPC_QUEUE_DEV', batch_count=16)
        print(f'fetched: {len(result)}')
        response_list = [DispatchResponseModel(correlation_id=request.correlation_id, status=DispatchResponseStatus.OK,
                                             data=request.data) for request in result]

        ds.batch_send_response(result, response_list)

def http_server():
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"code": 0}

    uvicorn.run(app, host="0.0.0.0", port=8000)



def main():
    # Creating child process using fork
    processid = os.fork()
    if processid:
        # This is the parent process
        # Closes file descriptor w
        print("Parent running")
        dispatch_server()
    else:
        # This is the child process
        print("Child running")
        http_server()

main()







