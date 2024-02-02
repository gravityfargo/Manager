import os
from git import Repo


def main():
    vault_dir = os.path.dirname(os.path.realpath(__file__))
    vault_dir_split = vault_dir.split("/")
    vault_dir = vault_dir.replace(vault_dir_split[-1], "")
    
    obsidian_dir = f"{vault_dir}.obsidian"
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
    checkForPlugins(community_plugins_config, required_plugins)

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


if __name__ == "__main__":
    main()