import subprocess

# Define servers and Python command
servers = [
    'pumpkin.cs.colostate.edu',
    'pepper.cs.colostate.edu',
    'potato.cs.colostate.edu',
]
python_command = 'python your_script.py'

# Start a new tmux session
session_name = "my_session"
subprocess.run(['tmux', 'new-session', '-d', '-s', session_name])

# Split the tmux window into two horizontal panes
subprocess.run(['tmux', 'split-window', '-v', '-t', session_name])
# In the first horizontal pane, split it vertically
subprocess.run(['tmux', 'split-window', '-h', '-t', f'{session_name}:0.0'])

# Send SSH commands to each pane
# Pane 0 (top left) for pumpkin server
subprocess.run(['tmux', 'send-keys', '-t', f'{session_name}:0.0', f'ssh {servers[0]}', 'C-m'])
subprocess.run(['tmux', 'send-keys', '-t', f'{session_name}:0.0', python_command, 'C-m'])

# Pane 1 (top right) for pepper server
subprocess.run(['tmux', 'send-keys', '-t', f'{session_name}:0.1', f'ssh {servers[1]}', 'C-m'])
subprocess.run(['tmux', 'send-keys', '-t', f'{session_name}:0.1', python_command, 'C-m'])

# Pane 2 (bottom) for potato server
# We will first select pane 2 because it defaults to pane 1 after the last split
subprocess.run(['tmux', 'select-pane', '-t', f'{session_name}:0.2'])
subprocess.run(['tmux', 'send-keys', f'ssh {servers[2]}', 'C-m'])
subprocess.run(['tmux', 'send-keys', python_command, 'C-m'])

# Attach to the session
subprocess.run(['tmux', 'attach-session', '-t', session_name])

print("Tmux session with split windows created successfully. Attached to session.")
