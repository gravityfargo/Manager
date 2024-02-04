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
        "templater-obsidian",
        "python-scripter",
        "dataview",
        "quickadd",
        "obsidian-local-rest-api",
        "cmdr",
    ]
    
    commander_config = {
        "id": "python-scripter:run-Manager",
        "icon": "command",
        "name": "Python Scripter: Run Manager",
        "mode": "any",
        "color": "#b152ff"
    }

    checkForPlugins(community_plugins_config, required_plugins)
    links_setup(executable_dir, visible_executable_dir)
    modify_commander(plugins_dir, commander_config)

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
        with open(conf, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Insert the new object into "leftRibbon"
        if "leftRibbon" in data:
            data["leftRibbon"].append(commander_config)
        else:
            raise Exception(f'"leftRibbon" key not found in {conf}')
        
        # Write the modified data back to the file
        with open(conf, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        print(f'Object inserted successfully into "leftRibbon" in {conf}')
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {conf}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
       
if __name__ == "__main__":
    main()