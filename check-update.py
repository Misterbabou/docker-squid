import requests
import re
import os
import sys

# Function to extract version and release from SOURCEURL
def extract_version_and_release(source_url):
    version = source_url.split('/')[4][1:]  # Extract Version
    release = source_url.split('/')[5].split('-')[1].rsplit('.', 2)[0] # Extract Release
    return version, release

# Function to fetch the latest version and release from the website
def fetch_latest_version_and_release(repo_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"  # Avoid anti-bot detection
    }
    url = f"https://api.github.com/repos/{repo_path}/releases/latest"
    # Make the GET request to the GitHub API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        latest_version = response.json()["name"]
        # Remove the 'v' prefix
        release = latest_version[1:]
        version, subversion = release.split('.')
        return version, release
    else:
        raise Exception(f"Failed to fetch releases: {response.status_code} - {response.text}")

# Function to update the Dockerfile with the new SOURCEURL
def update_dockerfile(dockerfile_path, new_source_url):
    with open(dockerfile_path, 'r') as file:
        lines = file.readlines()

    with open(dockerfile_path, 'w') as file:
        for line in lines:
            if line.startswith('ENV SOURCEURL='):
                # Update the line with the new SOURCEURL
                line = f'ENV SOURCEURL={new_source_url}\n'
            file.write(line)

def action_set_output(name, value):
    print("GitHub Actions: set output: " + name + "=" + value)

    if "GITHUB_OUTPUT" in os.environ:
        # See:
        # - https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter
        # - https://stackoverflow.com/a/74444094
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"{name}={value}\n")
    else:
        print("GITHUB_OUTPUT not set, skipping", file=sys.stderr)

def main():
    # Main logic
    dockerfile_path = 'Dockerfile'  # Path to the Dockerfile
    dockerfile_source_url = ""  # Initialize the SOURCEURL variable

    # Read the Dockerfile to get the current SOURCEURL
    with open(dockerfile_path, 'r') as file:
        for line in file:
            if line.startswith('ENV SOURCEURL='):
                dockerfile_source_url = line.split('=')[1].strip()  # Get the current SOURCEURL
                break

    # Extract current version and release from the Dockerfile's SOURCEURL
    current_version, current_release = extract_version_and_release(dockerfile_source_url)

    # Fetch the latest versions and releases from the website
    latest_version, latest_release = fetch_latest_version_and_release('squid-cache/squid')

    # Check if there are any versions found
    if latest_version and latest_release:
        print(f"Actual Version: {current_version} Release: {current_release}")
        print(f"Latest Version: {latest_version} Release: {latest_release}")

        # Compare versions and releases
        if (int(latest_version) > int(current_version)) or (int(latest_version) == int(current_version) and latest_release > current_release):
            print(f"Updating SOURCEURL to the latest version: v{latest_version} and release: {latest_release}")
            new_source_url = f"http://www.squid-cache.org/Versions/v{latest_version}/squid-{latest_release}.tar.gz"
            update_dockerfile(dockerfile_path, new_source_url)  # Update the Dockerfile
            action_set_output("new_version", latest_release)
        else:
            print("No update needed.")
    else:
        print("No versions found.")

if __name__ == "__main__":
    main()
