from l0n0ltcp.tcp_simple_proto import TcpSimpleProto
from l0n0ltcp.trans_callback import TransServerCallback, TransLocalServerCallback, TransServerClientCallback
from l0n0ltcp.tcp_server import TcpServer
from l0n0ltcp.socks5_callback import Socks5ServerCallback
from l0n0ltcp.socks5_proto import Socks5ServerProto
from l0n0ltcp.tcp_proto_base import TcpProtoBase
from l0n0ltcp.sym_enc_chacha20 import SymEncChaCha20
from l0n0ltcp.runner import run_forever
import argparse
import asyncio


def run_tsocks5_server():
    parser = argparse.ArgumentParser(description="创建SOCKS5服务器,并使用加密通道代理")
    parser.add_argument("listenhost", type=str, help="监听host")
    parser.add_argument("listenport", type=int, help="监听端口")
    parser.add_argument("password", type=str, help="密钥", default='')
    parser.add_argument("sock5port", type=str,
                        help="socks5监听端口(并不需要再启动一个socks5,自动启动一个socks5)", default=31234)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    sock5server = TcpServer('127.0.0.1', args.sock5port,
                            Socks5ServerCallback(),
                            Socks5ServerProto(),
                            loop=loop)
    sock5server.start()

    transserver = TcpServer(args.listenhost,
                            args.listenport,
                            TransServerCallback(
                                '127.0.0.1',
                                args.sock5port,
                                SymEncChaCha20(args.password)),
                            TcpSimpleProto(),
                            loop=loop)
    transserver.start()
    run_forever()


def run_socks5_server():
    parser = argparse.ArgumentParser(description="创建SOCKS5服务器(目前仅支持CONNECT命令)")
    parser.add_argument("listenhost", type=str, help="监听host")
    parser.add_argument("listenport", type=int, help="监听端口")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    sock5server = TcpServer(args.listenhost, args.listenport,
                            Socks5ServerCallback(),
                            Socks5ServerProto(),
                            loop=loop)
    sock5server.start()
    run_forever()


def run_trans_client():
    parser = argparse.ArgumentParser(description="创建本地代理服务器")
    parser.add_argument("serverhost", type=str, help="服务器监听host")
    parser.add_argument("serverport", type=int, help="服务器监听端口")
    parser.add_argument("localhost", type=str, help="本地服务host")
    parser.add_argument("localport", type=int, help="本地服务端口")
    parser.add_argument("password", type=str, help="密钥", default=b'')
    args = parser.parse_args()
    transserver = TcpServer(args.localhost, args.localport,
                            TransLocalServerCallback(
                                args.serverhost,
                                args.serverport,
                                SymEncChaCha20(args.password)),
                            TcpProtoBase(),
                            loop=asyncio.get_event_loop())
    transserver.start()
    run_forever()


def run_trans_server():
    parser = argparse.ArgumentParser(description="创建加密信道服务器")
    parser.add_argument("listenhost", type=str, help="监听host")
    parser.add_argument("listenport", type=int, help="监听端口")
    parser.add_argument("password", type=str, help="密钥", default='')
    parser.add_argument("targethost", type=str, help="要代理的host")
    parser.add_argument("targetport", type=str, help="要代理的端口")
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    transserver = TcpServer(args.listenhost, args.listenport,
                            TransServerCallback(
                                args.targethost,
                                args.targetport,
                                SymEncChaCha20(args.password)),
                            TcpSimpleProto(),
                            loop=loop)
    transserver.start()
    run_forever()
