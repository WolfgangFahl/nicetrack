'''
Created on 2023-08-16

@author: wf
'''
import sys
from argparse import ArgumentParser
from nicetrack.webserver import WebServer
from ngwidgets.cmd import WebserverCmd

class NiceTrackCmd(WebserverCmd):
    """
    nicetrack command line handling
    """
    
    def __init__(self):
        """
        constructor
        """
        config=WebServer.get_config()
        WebserverCmd.__init__(self, config, WebServer, DEBUG)
        pass

    def getArgParser(self,description:str,version_msg)->ArgumentParser:
        """
        override the default argparser call
        """        
        parser=super().getArgParser(description, version_msg)
        parser.add_argument("-v", "--verbose", action="store_true", help="show verbose output [default: %(default)s]")
        parser.add_argument("-rp", "--root_path",default=WebServer.examples_path(),help="path to pdf files [default: %(default)s]")
        return parser
    

def main(argv:list=None):
    """
    main call
    """
    cmd=NiceTrackCmd()
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())