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
def fetch_latest_version_and_release(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"  # Avoid anti-bot detection
    }
    response = requests.get(url, headers=headers)  # Include headers in the request
    if response.status_code == 200:
        html_content = response.text
        version_pattern = r'<tr>.*?<td><a href="v(\d+)/">\d+(?:\.\d+)?</a></td><td>.*?</td><td>(\d+\.\d+)</td>.*?</tr>'
        versions = re.findall(version_pattern, html_content, re.DOTALL)
        return versions
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

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
    latest_versions = fetch_latest_version_and_release('http://www.squid-cache.org/Versions/')

    # Check if there are any versions found
    if latest_versions:
        for version, release in latest_versions:
            print(f"Actual Version: {current_version} Release: {current_release}")
            print(f"Latest Version: {version} Release: {release}")

            # Compare versions and releases
            if (int(version) > int(current_version)) or (int(version) == int(current_version) and release > current_release):
                print(f"Updating SOURCEURL to the latest version: v{version} and release: {release}")
                new_source_url = f"http://www.squid-cache.org/Versions/v{version}/squid-{release}.tar.gz"
                update_dockerfile(dockerfile_path, new_source_url)  # Update the Dockerfile
                action_set_output("new_version", release)
                break
            else:
                print("No update needed.")
    else:
        print("No versions found.")

if __name__ == "__main__":
    main()
