import os
import requests
import base64
import hashlib
import argparse
import json

# Function to show the banner
def show_banner():
    banner = """
    ===========================================
               KGSFLINK 😊😊
          Follow on Instagram: gooalsahani666
    ===========================================
    """
    print(banner)

# Function to save the token for future use
def save_token(token):
    with open('config.json', 'w') as config_file:
        json.dump({'github_token': token}, config_file)

# Function to load the token if it exists
def load_token():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('github_token', None)
    return None

# Function to check if a repository exists
def check_repo_exists(repo_name, api_key):
    try:
        url = f'https://api.github.com/repos/{get_github_username(api_key)}/{repo_name}'
        headers = {
            'Authorization': f'token {api_key}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return False
        response.raise_for_status()  # Raise an error for non-200 responses
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error checking repository existence: {e}")
        return False

# Function to get GitHub username
def get_github_username(api_key):
    try:
        url = 'https://api.github.com/user'
        headers = {
            'Authorization': f'token {api_key}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['login']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub username: {e}")
        return None

# Function to create a new repository on GitHub
def create_github_repo(repo_name, api_key):
    try:
        url = 'https://api.github.com/user/repos'
        headers = {
            'Authorization': f'token {api_key}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'name': repo_name,
            'private': False  # Set to True if you want the repo to be private
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Repository '{repo_name}' created successfully.")
            return response.json()['html_url'], response.json()['full_name']
        else:
            print(f"Failed to create repository: {response.json()}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error creating repository: {e}")
        return None, None

# Function to get the SHA of a file in the repository
def get_file_sha(repo_full_name, file_path, api_key):
    try:
        url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
        headers = {
            'Authorization': f'token {api_key}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['sha']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file SHA: {e}")
        return None

# Function to calculate the SHA-1 hash of a local file
def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()
    except Exception as e:
        print(f"Error calculating SHA-1 for file {file_path}: {e}")
        return None

# Function to upload files to the repository
def upload_files_to_repo(repo_full_name, local_directory, api_key):
    url_template = f'https://api.github.com/repos/{repo_full_name}/contents/{{path}}'
    headers = {
        'Authorization': f'token {api_key}',
        'Accept': 'application/vnd.github.v3+json'
    }

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, local_directory)
            
            # Calculate the SHA-1 hash of the local file
            local_sha1 = calculate_sha1(file_path)
            if not local_sha1:
                print(f"Skipping {relative_path} due to error.")
                continue

            # Get the SHA of the file in the repository, if it exists
            remote_sha = get_file_sha(repo_full_name, relative_path, api_key)
            
            if remote_sha == local_sha1:
                print(f"Skipping {relative_path}, already exists with the same content.")
                continue
            
            # Print start of upload process
            print(f"Uploading {relative_path}...")
            
            try:
                with open(file_path, 'rb') as file:
                    content = base64.b64encode(file.read()).decode('utf-8')
                    data = {
                        'message': f"Add {relative_path}",
                        'content': content,
                        'branch': 'main'
                    }
                    response = requests.put(url_template.format(path=relative_path), json=data, headers=headers)
                    
                    if response.status_code == 201:
                        print(f"Uploaded {relative_path} successfully.")
                    else:
                        print(f"Failed to upload {relative_path}: {response.json()}")
            except Exception as e:
                print(f"Error uploading {relative_path}: {e}")

def main():
    # Show the banner
    show_banner()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="GitHub repo automation script.")
    parser.add_argument('-p', '--path', type=str, help="Path to the local directory to upload.")
    parser.add_argument('-A', '--api', type=str, help="GitHub API token.")
    args = parser.parse_args()

    # Load or save API token
    api_key = args.api
    if api_key:
        save_token(api_key)
    else:
        api_key = load_token()

    if not api_key:
        print("GitHub API token is required. Use '-A token' to provide it.")
        return

    # Ask for the repository name if not provided
    repo_name = input("Enter the name of the repository you want to create or upload to: ").strip()
    if not repo_name:
        print("Repository name is required.")
        return

    # Check if folder path is provided
    local_directory = args.path
    if not local_directory or not os.path.exists(local_directory):
        print("Folder path is required and must exist. Use '-p path' to provide it.")
        return

    # Check if the repository already exists
    if check_repo_exists(repo_name, api_key):
        print(f"Repository '{repo_name}' already exists. Uploading files to the existing repository.")
        repo_full_name = f"{get_github_username(api_key)}/{repo_name}"
    else:
        # Create the GitHub repository
        repo_url, repo_full_name = create_github_repo(repo_name, api_key)
        
        if not repo_url:
            print("Exiting script.")
            return

    # Upload the files from the directory to the repository
    upload_files_to_repo(repo_full_name, local_directory, api_key)

if __name__ == '__main__':
    main()
