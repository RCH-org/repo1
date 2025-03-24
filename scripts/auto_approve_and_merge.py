import os
from github import Github

# Load from environment
token = os.getenv("GITHUB_TOKEN")
org_name = os.getenv("ORGANIZATION_NAME")
author = os.getenv("GITHUB_USERNAME")

if not token or not org_name or not author:
    print("Missing env variables.")
    exit(1)

client = Github(token)
org = client.get_organization(org_name)

print(f"Searching PRs under org: {org_name} for user: {author}")

# Get all repos (excluding the automation source repo)
repos = [repo for repo in org.get_repos() if repo.name != "repo1"]

for repo in repos:
    print(f"Checking repository: {repo.name}")
    prs = repo.get_pulls(state="open")

    # Match PRs with branch name 'update-readthedocs'
    matched_prs = [pr for pr in prs if pr.head.ref == "update-readthedocs"]

    if not matched_prs:
        print(f"No matching PRs found in {repo.name}")
        continue

    for pr in matched_prs:
        print(f"Found PR #{pr.number} in {repo.name}")

        try:
            # Approve PR
            pr.create_review(event="APPROVE", body="Approved by automation")

            # Check if mergeable
            if pr.mergeable_state == "clean":
                pr.merge(merge_method="squash", commit_message="Squashed and merged by automation")
                print(f"Merged PR #{pr.number} in {repo.name}")
            else:
                print(f"Cannot merge PR #{pr.number} - state: {pr.mergeable_state}")

        except Exception as e:
            print(f"Error with PR #{pr.number} in {repo.name}: {e}")

print("PR approval and merge process completed!")
