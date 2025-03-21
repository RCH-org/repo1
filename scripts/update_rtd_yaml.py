import os
import subprocess
from github import Github

# Load PAT_GITHUB from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("ERROR: PAT_GITHUB is not set. Exiting...")
    exit(1)
else:
    print("PAT_GITHUB is set correctly!")

GITHUB_USERNAME = "rsagar-rch"
ORGANIZATION_NAME = "RCH-org"

# Authenticate with GitHub API
github_client = Github(GITHUB_TOKEN)
org = github_client.get_organization(ORGANIZATION_NAME)

# Get all repositories in the organization (except repo1)
repos = [repo for repo in org.get_repos() if repo.name != "repo1"]

# Define absolute path for `.readthedocs.yaml`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Moves from scripts/ to repo1/
SOURCE_FILE_PATH = os.path.join(BASE_DIR, "tests", ".readthedocs.yaml")

if not os.path.exists(SOURCE_FILE_PATH):
    print(f"ERROR: Source file '{SOURCE_FILE_PATH}' does not exist. Exiting...")
    exit(1)

for repo in repos:
    repo_name = repo.name
    repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{ORGANIZATION_NAME}/{repo_name}.git"

    print(f"Processing repository: {repo_name}")

    try:
        # Clone repo (shallow clone for speed)
        subprocess.run(["git", "clone", "--depth", "1", repo_url], check=True)
        os.chdir(repo_name)

        # Get default branch
        default_branch = repo.default_branch

        # Create a new branch
        subprocess.run(["git", "checkout", "-b", "update-readthedocs"], check=True)

        # Copy `.readthedocs.yaml` using Linux `cp` command
        subprocess.run(["cp", SOURCE_FILE_PATH, ".readthedocs.yaml"], check=True)

        # Add, commit, and push changes
        subprocess.run(["git", "add", ".readthedocs.yaml"], check=True)
        subprocess.run(["git", "commit", "-m", "Automated update: .readthedocs.yaml"], check=True)
        subprocess.run(["git", "push", "origin", "update-readthedocs"], check=True)

        # Create PR using GitHub API
        pr = repo.create_pull(
            title="Update .readthedocs.yaml",
            body="This PR updates the .readthedocs.yaml file to maintain compliance.",
            head="update-readthedocs",
            base=default_branch  # Dynamically set the base branch
        )

        # Assign reviewer
        pr.create_review_request(reviewers=["DeepakSawalka"])

        print(f"PR created successfully for {repo_name}")

    except subprocess.CalledProcessError as e:
        print(f"ERROR processing {repo_name}: {e}")
    
    finally:
        # Clean up - remove repo folder using Linux `rm -rf`
        os.chdir("..")
        subprocess.run(["rm", "-rf", repo_name], check=True)

print("All repositories updated successfully!")
