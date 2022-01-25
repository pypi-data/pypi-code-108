#!/usr/bin/env python3
import click 
@click.command()
@click.option('--port','-p',default=8080,help='端口设置')
@click.option('--ssl',default=False,help="采用ssl加密",is_flag=True)
@click.option('--flask',default=False,help="采用flask框架，默认是web.py框架",is_flag=True)
def main(port,ssl,flask):
    if not flask:
        from . import web_server as server
    else:
        from . import flask_server as server
    server.main(port,ssl)
if __name__=='__main__':
    main(8080,False,False)