import os
import subprocess
from urllib.parse import urlparse, unquote, urlunparse
import argparse
"""
def get_clean_repo_url_and_name(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')

    if len(path_parts) >= 2:
        user_part = path_parts[0]
        project_name = path_parts[1]
        clean_repo_url = urlunparse(parsed_url._replace(path=f'/{user_part}/{project_name}'))
        combined_name = f"{user_part}_{project_name}"
        return clean_repo_url, unquote(combined_name)
    return None, None
"""
def get_clean_repo_url_and_name(original_link):
    parsed_url = urlparse(original_link)
    path_segments = parsed_url.path.strip('/').split('/')
    
    # Make sure there are at least two segments (the user/organization and the repo name)
    if len(path_segments) < 2:
        return None, None
    
    repo_url = f'https://{parsed_url.netloc}/{path_segments[0]}/{path_segments[1]}'
    owner_name = path_segments[0]  # The first segment after 'github.com' is the directory name
    
    return repo_url, owner_name

def extract_links_from_file(file_path, unique_directories):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            original_link = line.strip()
            if original_link.startswith('http') and 'github.com' in original_link:
                repo_url, owner_name = get_clean_repo_url_and_name(original_link)
                if repo_url and owner_name:
                    unique_directories.add((owner_name, repo_url))



def main(update=False):
    project_url_file = "project_urls.txt"
    base_dir = 'projects'
    subdirectories = ['', 'src', 'src/example_code', 'scripts', 'Othello', 'Game', 'source', 'server', 'Server', 'Client']
    server_scripts = ['server.py', 'Server.py', 'Server', 'app-server.py', 'othello-server.py', 'TCP_server.py', 'TCPServer.py']
    client_scripts = ['client.py', 'Client.py', 'Client', 'app-client.py', 'othello-client.py', 'TCP_client.py', 'TCPClient.py']

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    unique_directories = set()



    # Extract links from HTML files
    #for filename in os.listdir(directory):
    #    if filename.endswith('.html') or filename.endswith('.htm'):
    extract_links_from_file(project_url_file, unique_directories)

    # Process each unique directory
    for directory_name, repo_url in unique_directories:
        full_directory_path = os.path.join(base_dir, directory_name)

        if os.path.exists(full_directory_path):
            if update:
                try:
                    subprocess.run(['git', 'stash'], check=True)
                    subprocess.run(['git', '-C', full_directory_path, 'pull'], check=True)
                except subprocess.CalledProcessError:
                    print(f"Failed to pull the latest changes in {full_directory_path}")
                    continue
        else:
            os.makedirs(full_directory_path)
            try:
                subprocess.run(['git', 'clone', repo_url, full_directory_path], check=True)
            except subprocess.CalledProcessError:
                print(f"Failed to clone {repo_url}")
                continue

            try:
                subprocess.run(['python', '-m', 'venv', os.path.join(full_directory_path, 'venv')], check=True)
            except subprocess.CalledProcessError:
                print(f"Failed to create virtual environment in {full_directory_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process URLs and update GitHub directories.")
    parser.add_argument("--update", action="store_true", help="Update existing GitHub directories with git pull.")
    args = parser.parse_args()

    main(update=args.update)
