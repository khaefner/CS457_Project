import libtmux
import time

class ProjectConnection:
    def __init__(self, servers, session_name="project_session"):
        # Store server details
        self.servers = servers
        self.session_name = session_name
        self.pane_mapping = {}

        # Initialize tmux server
        self.server = libtmux.Server()

        # Setup the tmux session
        #self.connect_or_create_session()

    def connect_or_create_session(self):
        # Check if the session already exists
        existing_session = self.server.has_session(self.session_name)
        if existing_session:
            print(f"Connecting to existing session '{self.session_name}'.")
            self.session = self.server.sessions.get(session_name=self.session_name)
            self.connect_to_existing_session()
        else:
            print(f"Creating and setting up a new session '{self.session_name}'.")
            self.setup_tmux_session()
    

    def setup_tmux_session(self):
        # Start a new tmux server and session
        self.session = self.server.new_session(session_name=self.session_name,attach=False)

        # Get the active window in the session
        self.window = self.session.active_window
        #self.window.set_window_option("window-style", "fg=colour247,bg=colour236")
        self.window.set_window_option("pane-border-style", "fg=colour235,bg=colour238")
        pane = self.window.attached_pane
        #self.session.attach()

    def connect_to_existing_session(self):
        self.session.attach()
        # Get the active window in the session
        self.window = self.session.active_window

    def send_echo(self):
        pane = self.window.active_pane
        pane.send_keys("echo 'Hello world'")

    def initial_connection(self, server_name, command):
        print("connected initial")
        pane = self.pane_mapping[server_name]
        # Clear the terminal and send the ssh command
        pane.send_keys(command, enter=True)
        pane.send_keys('clear', enter=True)

    def execute_command_on_one(self, server_name, command):
        pane = self.pane_mapping[server_name]
        # Send the command
        pane.send_keys(command, enter=True)

    def start_single(self):
        pane0 = self.window.active_pane
        self.pane_mapping = {
            'pumpkin': self.window.panes[0],
        }
        
    def execute_on_each_server(self,command):
        self.execute_command_on_one('pumpkin', command)
        self.execute_command_on_one('pepper', command)
        self.execute_command_on_one('potato', command)



    def start_multi(self,directory):


        server_cmd = "clear && echo 'Sleeping during pip install' && sleep 20 && clear && PS1='SERVER>' && echo '===============Running SERVER==================\n' && python server.py -p 12345 "
        client_cmd = "clear && echo 'Sleeping during pip install' && sleep 20 && clear && PS1='CLIENT>' && echo '===============Running CLIENT==================\n' && python client.py -i potato.cs.colostate.edu -p 12345 "
        # Split the window into two panes, top and bottom
        pane0 = self.window.active_pane
        self.window.split(attach=True, direction=libtmux.constants.PaneDirection.Above)

        # Split the top pane horizontally to create side-by-side panes for the first two servers
        pane1 = self.window.panes[0]
        pane1.split(attach=True, direction=libtmux.constants.PaneDirection.Right)
        # Map server names to their corresponding pane objects
        self.pane_mapping = {
            'pumpkin': self.window.panes[0],
            'pepper': self.window.panes[1],
            'potato': self.window.panes[2],
        }

        # Initial connection to servers
        self.initial_connection('pumpkin', f'ssh -Y {self.servers[0]}')
        self.initial_connection('pepper', f'ssh -Y {self.servers[1]}')
        self.initial_connection('potato', f'ssh -Y {self.servers[2]}')

        # Execute additional commands
        command = 'cd CS457_Project/projects/'+directory
        self.execute_on_each_server(command)

        #reset venv
        command = "rm -rf venv"
        self.execute_command_on_one('pumpkin',command)

        #create new venv
        command = "python3.11 -m venv venv"
        self.execute_command_on_one('pumpkin',command)
        #self.execute_on_each_server(command)
        
        #activate venv
        command = "source venv/bin/activate"
        self.execute_on_each_server(command)

        #activate venv
        command = "pip install --no-deps -r requirements.txt"
        self.execute_command_on_one('pumpkin',command)
        #self.execute_on_each_server(command)


        #run server on potato
        #command = "clear && echo 'Sleeping during pip install' && sleep 20 && python server.py -p 12345"
        command = server_cmd
        self.execute_command_on_one('potato',command)

        #run clients
        command = client_cmd
        self.execute_command_on_one('pepper',command)
        command = client_cmd
        self.execute_command_on_one('pumpkin',command)

        # Attach to the session
        self.session.attach()
        print("Tmux session with split windows created successfully. Attached to session.")
