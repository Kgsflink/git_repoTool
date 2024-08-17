### **GitHub Repository Management Script: Explanation and Usage Guide**

This script allows you to create a new GitHub repository and upload all files from a specified directory (and its subdirectories) to the repository. It also ensures that files are not uploaded multiple times by checking the content of existing files in the repository. Below is a detailed explanation of how to use this script and what you can do with it.

---

### **How to Use the Script**

#### **1. Prerequisites:**
   - **Python Installed**: Ensure you have Python installed on your system.
   - **GitHub Account**: You must have a GitHub account.
   - **GitHub Personal Access Token**: Generate a personal access token (PAT) from your GitHub account, which you will use as the API key. The token should have permissions to create repositories and upload content. Replace the placeholder `api_key` with your actual token.

#### **2. Setting Up:**
   - **Clone the Script**: Copy the script into a Python file, for example, `upload_to_github.py`.
   - **Modify the API Key**: Replace the `api_key` in the script with your GitHub personal access token.
   - **Set the Directory Path**: The script is set to upload files from `/storage/emulated/0/ApkEditor`. Ensure that this path points to the directory you want to upload.

#### **3. Running the Script:**
   - **Execute the Script**: Run the script from the command line or terminal:
     ```
     python upload_to_github.py
     ```
   - **Enter Repository Name**: When prompted, enter the name of the new repository you want to create.

#### **4. Viewing the Repository:**
   - **Check GitHub**: After the script runs, the new repository will be created on GitHub, and all the files from the specified directory will be uploaded. You can view your repository by visiting your GitHub account.

---

### **What This Script Can Do**

1. **Create a GitHub Repository:**
   - The script allows you to create a new GitHub repository directly from the command line. You can specify whether the repository is public or private.

2. **Upload Files to GitHub:**
   - The script will upload all files from a specified local directory to the newly created GitHub repository. It crawls through all subdirectories, ensuring the entire directory structure is preserved.

3. **Prevent Duplicate Uploads:**
   - Before uploading a file, the script checks whether the file already exists in the repository with the same content (using SHA-1 hash comparison). If it finds an identical file, it skips uploading that file. This feature is useful for avoiding redundant uploads and saving bandwidth.

4. **Monitor Upload Progress:**
   - The script prints messages to the console during the upload process, informing you about the progress and any issues that may occur, such as failed uploads.

---

### **Potential Use Cases**

- **Backup Local Projects:**
  - You can use this script to back up local project files to GitHub. By running the script periodically, only new or modified files will be uploaded, ensuring your repository stays up-to-date without unnecessary duplicates.

- **Automate Repository Creation:**
  - If you frequently start new projects, this script automates the process of creating a new GitHub repository and uploading initial project files.

- **Manage Multiple Directories:**
  - By modifying the `local_directory` variable, you can use this script to upload files from different directories, making it versatile for various projects or data sets.

- **Collaborative Development:**
  - For teams, this script can be used to upload and share codebases or data sets via GitHub, with the assurance that files won't be duplicated, streamlining collaboration.

---

### **Customizing the Script**

- **Change Repository Privacy:**
  - If you want the repository to be private, set `'private': True` in the `create_github_repo` function.

- **Upload Specific File Types:**
  - Modify the script to filter and upload only specific file types (e.g., `.py`, `.txt`) by adjusting the file-checking logic within the loop.

- **Add Custom Commit Messages:**
  - Customize the commit message for each file upload by altering the `data['message']` parameter in the `upload_files_to_repo` function.

---

This script provides a straightforward and efficient way to manage your GitHub repositories and upload files while ensuring that unnecessary duplicate uploads are avoided. It's a handy tool for developers and teams looking to streamline their GitHub workflows.
