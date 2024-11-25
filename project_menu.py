from simple_term_menu import TerminalMenu
from urllib.parse import urlparse
from project_connection import ProjectConnection
import subprocess
import sys

session_name = "project"
servers = [
    'pumpkin.cs.colostate.edu',
    'pepper.cs.colostate.edu',
    'potato.cs.colostate.edu',
]
pane_mapping = {
    'pumpkin': f'{session_name}:0.0',
    'pepper': f'{session_name}:0.1',
    'potato': f'{session_name}:0.2',
}


def read_urls_from_file(file_path):
    """Read the project names and URLs from the given file."""
    projects ={}

    with open(file_path, 'r') as file:
        for line in file:
            # Split each line by '|'
            parts = line.strip().split('|')
            
            #if there is a name on the team use that
            if len(parts) == 2:
                name, url = parts
                link = url.strip()
                parsed_url = urlparse(link)
                path_segments = parsed_url.path.strip('/').split('/')
            
                # Make sure there are at least two segments (the user/organization and the repo name)
                if len(path_segments) < 2:
                    return None, None
                
                #dir_name = path_segments[0]+'/'+path_segments[1]  # The first segment after 'github.com' is the directory name
                dir_name = path_segments[0]
                projects[name]=dir_name
            else:
                link = line.strip()
                parsed_url = urlparse(link)
                path_segments = parsed_url.path.strip('/').split('/')
            
                # Make sure there are at least two segments (the user/organization and the repo name)
                if len(path_segments) < 2:
                    return None, None
                
                #dir_name = path_segments[0]+'/'+path_segments[1]  # The first segment after 'github.com' is the directory name
                dir_name = path_segments[0]
                projects[dir_name] = dir_name


    
    return projects

def pull_projects(update=None):
    pull_connection = ProjectConnection(servers, session_name="pull_session")
    pull_connection.connect_or_create_session()
    pull_connection.start_single()
    pull_connection.initial_connection('pumpkin', f'ssh {servers[0]}')
    # cd to projects dir
    pull_connection.execute_command_on_one('pumpkin', 'cd CS457_Project')
    # Activate virtual environment
    pull_connection.execute_command_on_one('pumpkin', 'python3 -m venv venv')
    pull_connection.execute_command_on_one('pumpkin', 'source venv/bin/activate')
    if update:
        pull_connection.execute_command_on_one('pumpkin', 'python get_projects.py --update')
    else:
        pull_connection.execute_command_on_one('pumpkin', 'python get_projects.py')

    # connect to the tmux terminal
    subprocess.run(['tmux', 'attach-session', '-t', "pull_session"])


def run_project(directory):
    project_connection = ProjectConnection(servers, session_name="project_session")
    project_connection.connect_or_create_session()
    project_connection.start_multi(directory)

    # connect to the tmux terminal
    subprocess.run(['tmux', 'attach-session', '-t', "project_session"])


def main():
    # kill the tmux server
    subprocess.run(['tmux', 'kill-server'])

    file_path = 'project_urls.txt'  # Change this to your file path if necessary
    projects = read_urls_from_file(file_path)
    if not projects:
        print("The file contains no URLs.")
        return

    max_length = max(len(key) for key in projects.keys())

    # Create the options list with dynamically sized arrows
    options_list = [
        f"{key}{'-' * (max_length - len(key) + 5)}>:{value}"  
        for key, value in projects.items()
    ]
    options_list = sorted(options_list, key=str.lower)
    options_list.insert(0,f"┃|{'‾' * (int(max_length) +5+max_length)}"+"┃")
    options_list.insert(1,f"┃   -->Pull Projects {' ' * max_length}")
    options_list.insert(2,f"┃   -->Update Projects {' ' * max_length}")
    options_list.insert(3,f"┃|{'_' * (int(max_length) +5+max_length)}┃")


    # Create a terminal menu
    terminal_menu = TerminalMenu(options_list, title="Select a GitHub URL")
    menu_entry_index = terminal_menu.show()

    if menu_entry_index is not None:
        selected_url = options_list[menu_entry_index]
        if menu_entry_index == 1:
            pull_projects()
        elif menu_entry_index == 2:
            pull_projects(update=True)
        elif menu_entry_index == 3 or menu_entry_index == 0:
            main()
        else:
            project = selected_url.split(":")          
            run_project(project[1])
    else:
        print("No selection made.")


if __name__ == "__main__":
    main()
