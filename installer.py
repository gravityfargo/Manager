import os
from git import Repo


def main():
    vault_dir = os.path.dirname(os.path.realpath(__file__))
    obsidian_dir = f"{vault_dir}/.obsidian"
    community_plugins_config = f"{obsidian_dir}/community-plugins.json"
    required_plugins = [
        "templater-obsidian",
        "python-scripter",
        "dataview",
        "quickadd",
        "obsidian-local-rest-api",
        "cmdr",
    ]
    required_dirs = [
            f"{obsidian_dir}/scripts/python/"
    ]
    repo_url = "https://github.com/gravityfargo/Python-Obsidian-Manager.git"


    checkForPlugins(community_plugins_config, required_plugins)
    clone_repo(repo_url, )



def checkForPlugins(community_plugins_config, required_plugins):

    if os.path.isfile(community_plugins_config):
        with open(community_plugins_config, "r") as file:
            content = file.read()
        all_exist = all(item in content for item in required_plugins)
        if all_exist:
            print("Plugins are present")
        else:
            print("Required plugins are not installed and or enabled.")
    else:
        print("Required plugins are not installed and or enabled.")

def clone_repo(repo_url, destination):
    try:
        Repo.clone_from(repo_url, destination)
        print(f"Repository cloned into: {destination}")
    except Exception as e:
        print(f"Failed to clone repository: {e}")



if __name__ == "__main__":
    main()