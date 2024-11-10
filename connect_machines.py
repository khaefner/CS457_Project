import libtmux

# Define the server names and Python command
servers = [
    'pumpkin.cs.colostate.edu',
    'pepper.cs.colostate.edu',
    'potato.cs.colostate.edu',
]
python_command = 'python your_script.py'

# Start a new tmux server and session
server = libtmux.Server()
session = server.new_session(session_name="my_session", detach=True)

# Get the active window in the session
window = session.active_window

# Split the window into two panes, top and bottom
pane0 = window.active_pane
window.split(attach=True, direction=libtmux.constants.PaneDirection.Above)

# Split the top pane horizontally to create side-by-side panes for the first two servers
pane1 = window.panes[0]
pane1.split(attach=True,  direction=libtmux.constants.PaneDirection.Right)

# Map server names to their corresponding pane objects
pane_mapping = {
    'pumpkin': window.panes[0],
    'pepper': window.panes[1],
    'potato': window.panes[2],
}

def initial_connection(server_name, command):
    pane = pane_mapping[server_name]
    # Clear the terminal and send the ssh command
    pane.send_keys('clear', enter=True)
    pane.send_keys(command, enter=True)

def execute_command_in_pane(server_name, command):
    pane = pane_mapping[server_name]
    # Send the command
    pane.send_keys(command, enter=True)

# Initial connection
initial_connection('pumpkin', f'ssh {servers[0]}')
initial_connection('pepper', f'ssh {servers[1]}')
initial_connection('potato', f'ssh {servers[2]}')

# Execute additional command
execute_command_in_pane('potato', 'cd CS457_Project')

# Attach to the session
session.attach()

print("Tmux session with split windows created successfully. Attached to session.")
