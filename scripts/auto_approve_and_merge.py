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

# Get all the repos (skip source repo)
repos = [r for r in org.get_repos() if r.name != "repo1"]

for repo in repos:
    print(f"Checking repository: {repo.name}")
    prs = repo.get_pulls(state="open", head=f"{author}:update-readthedocs")

    if prs.totalCount == 0:
        print(f" No matching PRs found in {repo.name}")
        continue

    for pr in prs:
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
