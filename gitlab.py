import gitlab
import time
import os

# Constants
GITLAB_URL = "https://gitlab.com"  # Replace with your GitLab instance URL
ACCESS_TOKEN = "glpat-SZqaMSoycDHc5zb45zsn"
GROUP_NAME_PREFIX = "AutomatedGroup"
PROJECT_NAME = "AutomatedProject"
FILES_TO_UPLOAD = [
    "rrn.py",
    "config.py",
    "ranbal",
    "gitlab_ci_yml"
]  # Paths to your files
RUNTIME_LIMIT = 6 * 60 * 60  # 6 hours in seconds

# Initialize GitLab client
gl = gitlab.Gitlab(GITLAB_URL, private_token=ACCESS_TOKEN)

def create_new_group(group_name):
    """Create a new group in GitLab."""
    try:
        group = gl.groups.create({"name": group_name, "path": group_name.lower()})
        print(f"Group '{group_name}' created successfully.")
        return group
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to create group: {e}")
        return None

def create_project_in_group(group, project_name):
    """Create a new project in the specified group."""
    try:
        project = group.projects.create({"name": project_name})
        print(f"Project '{project_name}' created successfully.")
        return project
    except gitlab.exceptions.GitlabCreateError as e:
        print(f"Failed to create project: {e}")
        return None

def upload_files_to_project(project, file_paths):
    """Upload multiple files to the project repository."""
    try:
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            with open(file_path, "r") as f:
                file_content = f.read()
            project.files.create({
                "file_path": file_name,
                "branch": "main",
                "content": file_content,
                "commit_message": f"Add {file_name}",
            })
            print(f"File '{file_name}' uploaded successfully.")
    except Exception as e:
        print(f"Failed to upload files: {e}")

def create_pipeline_schedule(project):
    """Create a pipeline schedule for the project."""
    try:
        schedule = project.pipelineschedules.create({
            "description": "Automated pipeline schedule",
            "ref": "main",
            "cron": "0 * * * *",  # Adjust cron syntax as needed
        })
        print(f"Pipeline schedule created: {schedule}")
    except Exception as e:
        print(f"Failed to create pipeline schedule: {e}")

def delete_group(group):
    """Delete a group in GitLab."""
    try:
        group.delete()
        print(f"Group '{group.name}' deleted successfully.")
    except gitlab.exceptions.GitlabDeleteError as e:
        print(f"Failed to delete group: {e}")

def main():
    while True:
        # Step 1: Create a unique group name
        group_name = f"{GROUP_NAME_PREFIX}_{int(time.time())}"

        # Step 2: Create a new group
        group = create_new_group(group_name)
        if not group:
            continue

        # Step 3: Create a project in the group
        project = create_project_in_group(group, PROJECT_NAME)
        if not project:
            continue

        # Step 4: Upload files to the project
        upload_files_to_project(project, FILES_TO_UPLOAD)

        # Step 5: Create a pipeline schedule
        create_pipeline_schedule(project)

        # Step 6: Wait for 6 hours (runtime limit)
        print(f"Group '{group.name}' is running. Waiting for {RUNTIME_LIMIT / 3600} hours...")
        time.sleep(RUNTIME_LIMIT)

        # Step 7: Delete the group after runtime limit is reached
        delete_group(group)

if __name__ == "__main__":
    main()
