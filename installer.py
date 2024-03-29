import os, json


def main():
    vault_dir = os.path.dirname(os.path.realpath(__file__))
    vault_dir_split = vault_dir.split("/")
    vault_dir = vault_dir.replace(vault_dir_split[-1], "")

    obsidian_dir = f"{vault_dir}.obsidian"
    scripts_dir = f"{obsidian_dir}/scripts/python"
    plugins_dir = f"{obsidian_dir}/plugins"
    executable_dir = f"{scripts_dir}/Manager"
    community_plugins_config = f"{obsidian_dir}/community-plugins.json"
    visible_executable_dir = f"{vault_dir}Manager"

    required_plugins = [
        "python-scripter",
        "dataview",
        "obsidian-local-rest-api",
        "cmdr",
        "obsidian-tasks-plugin",
        "multi-column-markdown",
        "editor-width-slider",
    ]

    commander_config = {
        "id": "python-scripter:run-Manager",
        "icon": "command",
        "name": "Python Scripter: Run Manager",
        "mode": "any",
        "color": "#b152ff",
    }

    checkForPlugins(community_plugins_config, required_plugins)
    links_setup(executable_dir, visible_executable_dir)
    modify_commander(plugins_dir, commander_config)
    modify_rest_api(plugins_dir)
    modify_obsidian_config(obsidian_dir)


def checkForPlugins(community_plugins_config, required_plugins):
    if os.path.isfile(community_plugins_config):
        with open(community_plugins_config, "r") as file:
            content = file.read()
        all_exist = all(item in content for item in required_plugins)
        if all_exist:
            print("Plugins are present")
        else:
            raise Exception("Required plugins are not installed and or enabled.")
    else:
        raise Exception("Required plugins are not installed and or enabled.")


def links_setup(executable_dir, visible_executable_dir):
    os.makedirs(executable_dir, exist_ok=True)
    entries = os.listdir(visible_executable_dir)
    for entry in entries:
        if not entry.startswith("."):
            source = visible_executable_dir + "/" + entry
            symlink_path = executable_dir + "/" + entry

            if not os.path.islink(symlink_path):
                os.symlink(source, symlink_path)
                print(f"Symlink created: {symlink_path} -> {source}")
            else:
                print("Symlink already exists.")


def modify_commander(plugins_dir, commander_config):
    try:
        conf = f"{plugins_dir}/cmdr/data.json"
        with open(conf, "r", encoding="utf-8") as file:
            data = json.load(file)

        if "leftRibbon" in data:
            data["leftRibbon"].append(commander_config)

        with open(conf, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Launch icon added to the left ribbon.")
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {conf}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def modify_rest_api(plugins_dir):
    try:
        conf = f"{plugins_dir}/obsidian-local-rest-api/data.json"
        with open(conf, "r", encoding="utf-8") as file:
            data = json.load(file)

        data["enableInsecureServer"] = "true"

        with open(conf, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("REST API Insecure Server Enabled")
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {conf}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def modify_obsidian_config(obsidian_dir):
    try:
        conf = f"{obsidian_dir}/custom-config.json"
        if not os.path.exists(conf):
            data = {}
        else:
            with open(conf, "r", encoding="utf-8") as file:
                data = json.load(file)
        data.update(
            {
                "newFileLocation": "current",
                "alwaysUpdateLinks": "true",
                "trashOption": "local",
                "showInlineTitle": "false",
                "promptDelete": "false",
                "readableLineLength": "true",
                "useMarkdownLinks": "false",
                "attachmentFolderPath": "Manager/Attachments",
            }
        )

        with open(conf, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Obsidian custom configuration updated.")
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {conf}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
