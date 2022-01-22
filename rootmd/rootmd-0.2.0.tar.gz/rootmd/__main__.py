#!/usr/bin/env conda run -n py38 python

import html
import os
import mistletoe as md
from mistletoe.ast_renderer import ASTRenderer
from rich import inspect
from rich.console import Console
from rich.markdown import Markdown
from rich.logging import RichHandler
import logging
import argparse
from rootmd import RootHtmlRenderer
from rootmd import RootMdRenderer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

observer = Observer()



FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


"""
Entry point for RootMd
"""
parser = argparse.ArgumentParser(description='Convert Markdown with inline c++ code to ROOT output.')
parser.add_argument('input', help='Markdown file')
parser.add_argument('-o', '--output', help='output filename  default <in>.html', default="")
parser.add_argument('-f', '--format', help='output format', default="html", choices=["html", "md", "obsidian", "json", "terminal"])
parser.add_argument('-e', '--embed', help='embed images as base 64', default=False, action="store_true")
parser.add_argument('-a', '--asset-dir', help='specify asset output directory, paths are NOTE re-written to support unless using obsidian format', default="")
parser.add_argument('-v', '--verbosity', help='specify log verbosity', default=0, type=int)
parser.add_argument( '-w', '--watch', help='watch a file or directory for changes')

args = parser.parse_args()


EXTENSIONS = {
    "html"     : ".html",
    "md"       : ".md",
    "obsidian" : ".md",
    "json"     : ".json",
    "terminal" : ".md"
}


console = Console()

log.setLevel( logging.INFO )
VERBOSITY = args.verbosity
if VERBOSITY >= 10 :
    log.setLevel( logging.DEBUG )
if VERBOSITY >= 20 :
    log.setLevel( logging.INFO )
if VERBOSITY >= 30 :
    log.setLevel( logging.WARNING )
if VERBOSITY >= 40 :
    log.setLevel( logging.ERROR )
if VERBOSITY >= 50 :
    log.setLevel( logging.CRITICAL )


ASSET_PREFIX=""
EMBED = args.embed
ASSET_DIR = args.asset_dir
if args.output == "":
    args.output = args.input  + EXTENSIONS[args.format]# ext will be added later

# if VERBOSITY <= 1:
#     inspect( args )

basename = os.path.basename( args.output )

# handle obsidian's way of removing the attachment/ (or whatever dir) from paths
if args.format == "obsidian":
    ASSET_PREFIX = os.path.splitext(basename)[0]
    ASSET_DIR = os.path.join( ASSET_DIR, ASSET_PREFIX )
    if not os.path.isdir( ASSET_DIR ):
        log.info( "Making asset directory: %s" % ASSET_DIR )
        os.mkdir( ASSET_DIR )





class RootMd :
    def __init__(self, *args, **kwargs) -> None:
        log.debug("args:")
        # inspect( args[0] )
        self.args = args[0]
        log.debug( self.args.input )
        self.title = ""
        self.last_run_input = ""
        self.last_run_time = 0

    def run(self, input):
        delta_time = time.time() - self.last_run_time
        self.args.input = input
        # log.info( "delta_time = %d" % delta_time )
        if self.args.input == self.last_run_input and delta_time < 4 :
            return
        self.last_run_input = self.args.input
        self.last_run_time = time.time()
        
        if not os.path.exists(self.args.input) :
            log.error("File %s does not exist" % ( self.args.input ) )
            return
        
        log.info( "Processing %s to %s output format" % (self.args.input, self.args.format ) )
        self.title = args.input
        theRenderer = RootHtmlRenderer()
        theRenderer.set( embed=EMBED, asset_dir=ASSET_DIR, asset_prefix=ASSET_PREFIX )
        
        if args.format == "md" or args.format == "obsidian" or args.format == "terminal":
            theRenderer = RootMdRenderer()
            theRenderer.set( embed=EMBED, asset_dir=ASSET_DIR, asset_prefix=ASSET_PREFIX )
        if args.format == "ast" :
            theRenderer = ASTRenderer()

        with open( args.input , 'r') as fin:
            html = theRenderer.render(md.Document(fin))

        if args.format == "terminal" :
            console.print( Markdown(html) )
            return

        output = args.output
        if "" == output :
            output = args.input + "." + args.format

        log.info( "Writing output to %s" % output )
        with open( output , "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
            output_file.write(html)

            

rootmd = RootMd(args)


class Handler(FileSystemEventHandler):
  
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'modified' :
            # inspect( event )
            # Event is modified, you can process it now
            log.info("Watchdog received modified event - % s." % event.src_path)
            rootmd.run(input=event.src_path)


if args.watch :
    event_handler = Handler()
    observer.schedule(event_handler, args.watch, recursive = True)
    log.info( 'Watching "%s" for changes' % args.watch )
    observer.start()
    try:
        while True:
            time.sleep(5)
    except:
        observer.stop()
        # print("Observer Stopped")

    observer.join()
    exit()


rootmd.run(args.input)