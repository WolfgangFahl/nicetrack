"""
Created on 2023-06-19

@author: wf
"""
from typing import Optional
from nicesrt.version import Version
from nicesrt.leaflet import leaflet
from nicesrt.srt import SRT
from nicesrt.local_filepicker import LocalFilePicker
from nicesrt.file_selector import FileSelector
from nicegui import ui, Client

import os
import sys
import requests
import traceback

class WebServer:
    """
    WebServer class that manages the server 
    
    """

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        self.is_local=False
        self.log_view=None
        self.do_trace=True
        self.input=""
        self.srt=None
        
        @ui.page('/')
        async def home(client: Client):
            await self.home(client)
            
        @ui.page('/settings')
        def settings():
            self.settings()
            
            
    @classmethod
    def examples_path(cls)->str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), '../nicesrt_examples')
        path = os.path.abspath(path)
        return path
 
    def handle_exception(self, e: BaseException, trace: Optional[bool] = False):
        """Handles an exception by creating an error message.

        Args:
            e (BaseException): The exception to handle.
            trace (bool, optional): Whether to include the traceback in the error message. Default is False.
        """
        if trace:
            self.error_msg = str(e) + "\n" + traceback.format_exc()
        else:
            self.error_msg = str(e)
        if self.log_view:
            self.log_view.push(self.error_msg)
        print(self.error_msg,file=sys.stderr)

    async def render(self, _click_args=None):
        """
        Renders the SRT content

        Args:
            click_args (object): The click event arguments.
        """
        try:
            ui.notify(f"rendering srt {self.input}")
            srt_text=self.do_read_input(self.input)
            self.srt=SRT.from_text(srt_text)
            self.geo_path=self.srt.as_geopath()
            with self.geo_map as geo_map:
                path=self.geo_path.get_path()
                if len(path)>0:
                    loc=path[0]
                    geo_map.set_location(loc)
                    print(f"setting location to {loc}")
                    geo_map.draw_path(path)
            # show render result in log
            #self.log_view.push(render_result.stderr)
        except BaseException as ex:
            self.handle_exception(ex,self.do_trace)  
            
    def do_read_input(self, input_str: str):
        """Reads the given input.

        Args:
            input_str (str): The input string representing a URL or local path.
        """
        if input_str.startswith('http://') or input_str.startswith('https://'):
            response = requests.get(input_str)
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f'Unable to retrieve data from URL: {input_str}')
        else:
            if os.path.exists(input_str):
                with open(input_str, 'r') as file:
                    return file.read()
            else:
                raise Exception(f'File does not exist: {input_str}')
    
    async def read_and_optionally_render(self,input_str):
        """Reads the given input and optionally renders the given input

        Args:
            input_str (str): The input string representing a URL or local file.
        """
        self.input_input.set_value(input_str)
        self.read_input(input_str)
        if self.render_on_load:
            await self.render(None)
        
    def read_input(self, input_str: str):
        """Reads the given input and handles any exceptions.

        Args:
            input_str (str): The input string representing a URL or local file.
        """
        try:
            ui.notify(f"reading {input_str}")
            if self.log_view:
                self.log_view.clear()
            self.error_msg = None
        except BaseException as e:
            self.handle_exception(e, self.do_trace)
            
    async def open_file(self) -> None:
        """Opens a Local filer picker dialog and reads the selected input file."""
        if self.is_local:
            pick_list = await LocalFilePicker('~', multiple=False)
            if pick_list and len(pick_list)>0:
                input_file=pick_list[0]
                await self.read_and_optionally_render(input_file)
    pass
         
    async def reload_file(self):
        """
        reload the input file
        """
        input_str=self.input
        if os.path.exists(input_str):
            input_str=os.path.abspath(input_str)
        allowed_urls=[
            "https://raw.githubusercontent.com/JuanIrache/DJI_SRT_Parser/master/samples/",
            "https://raw.githubusercontent.com/JuanIrache/dji-srt-viewer/master/samples/",
            self.examples_path(),
            self.root_path
        ]
        allowed=self.is_local
        if not self.is_local:
            for allowed_url in allowed_urls:
                if input_str.startswith(allowed_url):
                    allowed=True
        if not allowed:
            ui.notify("only white listed URLs and Path inputs are allowed")
        else:    
            await self.read_and_optionally_render(self.input)
    
    def link_button(self, name: str, target: str, icon_name: str,new_tab:bool=True):
        """
        Creates a button with a specified icon that opens a target URL upon being clicked.
    
        Args:
            name (str): The name to be displayed on the button.
            target (str): The target URL that should be opened when the button is clicked.
            icon_name (str): The name of the icon to be displayed on the button.
            new_tab(bool): if True open link in new tab
    
        Returns:
            The button object.
        """
        with ui.button(name,icon=icon_name) as button:
            # new_tab parameter not used yet
            button.on("click",lambda: (ui.open(target)))
        return button
    
    
    def tool_button(self,tooltip:str,icon:str,handler:callable=None,toggle_icon:str=None)->ui.button:
        """
        Creates an  button with icon that triggers a specified function upon being clicked.
    
        Args:
            tooltip (str): The tooltip to be displayed.
            icon (str): The name of the icon to be displayed on the button.
            handler (function): The function to be called when the button is clicked.
            toggle_icon (str): The name of an alternative icon to be displayed when the button is clicked.
    
        Returns:
            ui.button: The icon button object.
            
        valid icons may be found at:    
            https://fonts.google.com/icons
        """
        icon_button=ui.button("",icon=icon, color='primary').tooltip(tooltip).on("click",handler=handler)  
        icon_button.toggle_icon=toggle_icon
        return icon_button   
        
    def setup_menu(self):
        """Adds a link to the project's GitHub page in the web server's menu."""
        with ui.header() as self.header:
            self.link_button("home","/","home")
            self.link_button("settings","/settings","settings")
            self.link_button("github",Version.cm_url,"bug_report")
            self.link_button("chat",Version.chat_url,"chat")
            self.link_button("help",Version.doc_url,"help")
    
    def setup_footer(self):
        """
        setup the footer
        """
        with ui.footer() as self.footer:
            ui.label("(c)2023 Wolfgang Fahl")
            ui.link("Powered by nicegui","https://nicegui.io/").style("color: #fff") 
  
    def input_changed(self,cargs):
        """
        react on changed input
        """
        self.input=cargs.value
        pass
    
    def toggle_icon(self,button:ui.button):
        """
        toggle the icon of the given button
        
        Args:
            ui.button: the button that needs the icon to be toggled
        """
        if hasattr(button,"toggle_icon"):
            # exchange icon with toggle icon
            toggle_icon=button._props["icon"]
            icon=button.toggle_icon
            button._props["icon"]=icon
            button.toggle_icon=toggle_icon
        button.update()
        
    async def home(self, client:Client):
        """Generates the home page with a map"""
        self.setup_menu()
    
        with ui.element("div").classes("w-full"):
            self.example_selector=FileSelector(path=self.root_path,handler=self.read_and_optionally_render)
            self.input_input=ui.input(
                value=self.input,
                on_change=self.input_changed).props("size=100")
            self.tool_button(tooltip="reload",icon="refresh",handler=self.reload_file)    
            if self.is_local:
                self.tool_button(tooltip="open",icon="file_open",handler=self.open_file)
        with leaflet().classes('w-full h-96') as self.geo_map:
                pass   
        
        self.setup_footer()        
        if self.args.input:
            #await client.connected()
            await self.read_and_optionally_render(self.args.input)
        
    def settings(self):
        """Generates the settings page with a link to the project's GitHub page."""
        self.setup_menu()
        ui.checkbox('debug with trace', value=True).bind_value(self, "do_trace")
        ui.checkbox('render on load',value=self.render_on_load).bind_value(self,"render_on_load")
        self.setup_footer()
       
    def run(self, args):
        """Runs the UI of the web server.

        Args:
            args (list): The command line arguments.
        """
        self.args=args
        self.input=args.input
        self.is_local=args.local
        self.root_path=os.path.abspath(args.root_path) 
        self.render_on_load=args.render_on_load
        ui.run(title=Version.name, host=args.host, port=args.port, show=args.client,reload=False)
