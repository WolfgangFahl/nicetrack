'''
Created on 2023-08-16

@author: wf
'''
import sys
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