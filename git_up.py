import os
import requests
import base64
import hashlib
import argparse
import json
import time

# ========================== Helper Functions ==========================

def show_banner():
    """Displays the welcome banner."""
    banner = """
    ===========================================
               GITHUB UPLOAD TOOL
          Professional Automation Script
    ===========================================
    """
    print(banner)

def save_token(token):
    """Save the API token to a config file."""
    with open('config.json', 'w') as config_file:
        json.dump({'github_token': token}, config_file)

def load_token():
    """Load the API token from the config file."""
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                return config.get('github_token', None)
    except (json.JSONDecodeError, KeyError) as e:
        print("Error reading token from config.json. Resetting the file.")
        save_token("")
    return None

# ========================== GitHub Functions ==========================

def get_github_username(api_key):
    """Get the GitHub username of the user."""
    try:
        url = 'https://api.github.com/user'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('login', None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub username: {e}")
        return None

def check_repo_exists(repo_name, api_key):
    """Check if the repository exists on GitHub."""
    try:
        url = f'https://api.github.com/repos/{get_github_username(api_key)}/{repo_name}'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.get(url, headers=headers)
        return response.status_code != 404
    except requests.exceptions.RequestException as e:
        print(f"Error checking repository existence: {e}")
        return False

def create_github_repo(repo_name, api_key):
    """Create a new repository on GitHub."""
    try:
        url = 'https://api.github.com/user/repos'
        headers = {'Authorization': f'token {api_key}'}
        data = {'name': repo_name, 'private': False}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Repository '{repo_name}' created successfully.")
            return response.json().get('full_name')
        else:
            print(f"Failed to create repository: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating repository: {e}")
    return None

def get_file_sha(repo_full_name, file_path, api_key):
    """Get the SHA and content of a file in the GitHub repository."""
    try:
        url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('sha'), base64.b64decode(response.json().get('content'))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file SHA: {e}")
    return None, None

# ========================== File Functions ==========================

def calculate_sha1(file_path):
    """Calculate the SHA-1 hash of a local file."""
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()
    except Exception as e:
        print(f"Error calculating SHA-1 for file {file_path}: {e}")
    return None

def upload_files_to_repo(repo_full_name, local_directory, api_key, ignore_list):
    """Upload or update files to the GitHub repository, creating folders as needed."""
    url_template = f'https://api.github.com/repos/{repo_full_name}/contents/{{path}}'
    headers = {'Authorization': f'token {api_key}'}

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, local_directory)

            if any(ignored in relative_path for ignored in ignore_list):
                print(f"Skipping ignored file: {relative_path}")
                continue

            try:
                print(f"Processing file: {relative_path}")
                sha, remote_content = get_file_sha(repo_full_name, relative_path, api_key)

                with open(file_path, 'rb') as file:
                    content = base64.b64encode(file.read()).decode('utf-8')

                if remote_content and remote_content == base64.b64decode(content):
                    print(f"No changes in {relative_path}. Skipping.")
                    continue

                url = url_template.format(path=relative_path)
                data = {'message': f"Upload {relative_path}", 'content': content, 'branch': 'main'}
                if sha:
                    data['sha'] = sha

                attempt = 0
                success = False
                while attempt < 3 and not success:
                    try:
                        response = requests.put(url, json=data, headers=headers)
                        if response.status_code in [200, 201]:
                            print(f"Successfully uploaded {relative_path}")
                            success = True
                        else:
                            print(f"Failed to upload {relative_path}: {response.json()}")
                            attempt += 1
                            time.sleep(5)
                    except requests.exceptions.RequestException as e:
                        print(f"Network error during upload of {relative_path}: {e}")
                        attempt += 1
                        time.sleep(5)

                if not success:
                    print(f"Failed to upload {relative_path} after multiple attempts.")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# ========================== Main Script ==========================

def main():
    show_banner()
    parser = argparse.ArgumentParser(description="GitHub repo automation script.")
    parser.add_argument('-p', '--path', type=str, help="Path to the local directory to upload.")
    parser.add_argument('-A', '--api', type=str, help="GitHub API token to save.")
    parser.add_argument('-I', '--ignore', type=str, nargs='*', help="Files or folders to ignore.")
    args = parser.parse_args()

    if args.api:
        save_token(args.api)
        print("GitHub API token has been saved successfully!")

    api_key = load_token()
    if not api_key:
        print("GitHub API token is required. Please set it using -A flag.")
        return

    if not args.path:
        print("Path to the local directory is required. Use -p to specify the path.")
        return

    repo_name = input("Enter the name of the repository to create or upload to: ").strip()
    if not repo_name:
        print("Repository name is required.")
        return

    local_directory = args.path
    if not os.path.exists(local_directory):
        print("Invalid path provided.")
        return

    ignore_list = args.ignore if args.ignore else []

    if check_repo_exists(repo_name, api_key):
        repo_full_name = f"{get_github_username(api_key)}/{repo_name}"
        print(f"Repository '{repo_name}' already exists.")
    else:
        repo_full_name = create_github_repo(repo_name, api_key)
        if not repo_full_name:
            print("Exiting script.")
            return

    upload_files_to_repo(repo_full_name, local_directory, api_key, ignore_list)

if __name__ == '__main__':
    main()
