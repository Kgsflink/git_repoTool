import os
import requests
import base64
import hashlib
import time

# GitHub API key
api_key = 'ghp_yFPhrnSCMiv3NsYj1ffwkSa79LLJXqv01D3FVF'

# Function to check if a repository exists
def check_repo_exists(repo_name):
    url = f'https://api.github.com/repos/{get_github_username()}/{repo_name}'
    headers = {
        'Authorization': f'token {api_key}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    
    return response.status_code == 200

# Function to get GitHub username
def get_github_username():
    url = 'https://api.github.com/user'
    headers = {
        'Authorization': f'token {api_key}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()['login']
    else:
        raise Exception("Failed to retrieve GitHub username")

# Function to create a new repository on GitHub
def create_github_repo(repo_name):
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

# Function to get the SHA of a file in the repository
def get_file_sha(repo_full_name, file_path):
    url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
    headers = {
        'Authorization': f'token {api_key}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()['sha']
    return None

# Function to calculate the SHA-1 hash of a local file
def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

# Function to upload files to the repository
def upload_files_to_repo(repo_full_name, local_directory):
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
            
            # Get the SHA of the file in the repository, if it exists
            remote_sha = get_file_sha(repo_full_name, relative_path)
            
            # Skip the upload if the file already exists with the same content
            if remote_sha == local_sha1:
                print(f"Skipping {relative_path}, already exists with the same content.")
                continue
            
            # Print start of upload process
            print(f"Uploading {relative_path}...")
            
            with open(file_path, 'rb') as file:
                content = base64.b64encode(file.read()).decode('utf-8')
                data = {
                    'message': f"Add {relative_path}",
                    'content': content,
                    'branch': 'main'
                }
                
                # Include the SHA if updating an existing file
                if remote_sha:
                    data['sha'] = remote_sha
                
                # Attempt the request with retries
                for attempt in range(3):
                    try:
                        response = requests.put(url_template.format(path=relative_path), json=data, headers=headers)
                        
                        if response.status_code in {201, 200}:
                            print(f"Uploaded {relative_path} successfully.")
                            break
                        else:
                            print(f"Failed to upload {relative_path}: {response.json()}")
                            break
                    except requests.exceptions.SSLError as e:
                        print(f"SSL error on {relative_path}, retrying... ({attempt + 1}/3)")
                        time.sleep(2)  # Wait before retrying
                    except Exception as e:
                        print(f"Error uploading {relative_path}: {e}")
                        break

def main():
    # Ask for the repository name
    repo_name = input("Enter the name of the repository you want to create or upload to: ")

    # Define the directory to upload
    local_directory = '/storage/emulated/0/ApkEditor'

    # Check if the repository already exists
    if check_repo_exists(repo_name):
        print(f"Repository '{repo_name}' already exists. Uploading files to the existing repository.")
        repo_full_name = f"{get_github_username()}/{repo_name}"
    else:
        # Create the GitHub repository
        repo_url, repo_full_name = create_github_repo(repo_name)
        
        if not repo_url:
            print("Exiting script.")
            return

    # Upload the files from the directory to the repository
    upload_files_to_repo(repo_full_name, local_directory)

if __name__ == '__main__':
    main()
