#!/usr/bin/env python3

"""
protobuf 搭配 grpc 来实现序列号服务器
"""

import sys
import grpc
import logging
import argparse
from concurrent import futures
from threading import RLock

from pbes import sequense_pb2
from pbes import sequense_pb2_grpc

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(lineno)s - %(message)s")

name = "sequence-server"

def parse():
    parser = argparse.ArgumentParser(name)
    parser.add_argument("--ip",type=str,default="127.0.0.1")
    parser.add_argument("--port",type=int,default=10352)
    parser.add_argument("action",type=str,default="exit",choices=["exit","run"])
    return parser.parse_args()

class SeqenceServer(sequense_pb2_grpc.SequenceServer):
    current = 0
    lock = RLock()
    def get(self,request,context):
        """
        """
        logging.info(f"revice request from {context.peer()} offset = {request.offset} .")
        logging.info(f"current = {self.current} .")
        with self.lock:
            self.current = self.current + (request.offset if request.offset != 0 else 1)
            return sequense_pb2.SequenceResponse(sequence=self.current)

def serve():
    # 处理请求参数
    args = parse()
    if args.action == "exit":
        logging.warning("exit bye .")
        sys.exit(0)
    
    host = args.ip
    port = args.port

    logging.info(f"sequence-server start listen on {host}:{port} .")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sequense_pb2_grpc.add_SequenceServerServicer_to_server(SeqenceServer(), server)
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    logging.info("seqense-server started .")
    server.wait_for_termination()
