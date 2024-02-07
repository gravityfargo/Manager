import sys, json, os, requests
import shutil
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QApplication,
    QMainWindow,
)
import PDF_Processor, New_Note


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.noteCreatorWindows = []
        self.initVars()
        self.create_dirs(
            self.directory_config_json,
            self.configs["root-dirs"],
            self.configs["vault_root_directory"],
        )
        self.create_indexes(
            self.directory_config_json,
            self.configs["root-dirs"],
            self.configs["vault_root_directory"],
            self.templates,
        )
        self.setWindowTitle("Obsidian Manager")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.setupUI()

        self.index_directory()

    def setupUI(self):
        self.createNoteButton = QPushButton("Create Note")
        self.createNoteButton.clicked.connect(self.launchCreateNote)
        self.layout.addWidget(self.createNoteButton)

        self.importNoteButton = QPushButton("Import Note")
        self.importNoteButton.clicked.connect(self.launchImportNote)
        self.layout.addWidget(self.importNoteButton)

        self.process_pdf_button = QPushButton("Process PDF")
        # self.process_pdf_button.clicked.connect(self.launchProcessPDF)
        self.layout.addWidget(self.process_pdf_button)

    def launchCreateNote(self):
        noteCreator = New_Note.NoteCreator(
            self.configs, self.directory_config_json, self.templates, "Create Note"
        )
        noteCreator.dataSent.connect(self.handleNoteCreatorData)
        noteCreator.show()
        self.noteCreatorWindows.append(noteCreator)

    def handleNoteCreatorData(self, data):
        if data["type"] == "new_note":
            data["prefix"] = "/vault"
            self.put_request(data, self.put_new_note_headers)
            data["prefix"] = "/open"
            data["content"] = ""
            self.post_request(data, self.post_headers)

    def launchImportNote(self):
        self.noteImporter = New_Note.NoteCreator(
            self.configs, self.directory_config_json, "Import Note"
        )
        self.noteImporter.show()

    def initVars(self):
        manager_directory, vault_root_directory = self.get_vault_path()
        # /home/nathan/TEMPVAULT/Manager/
        # /home/nathan/TEMPVAULT/
        (
            primary_config_json,
            self.directory_config_json,
            self.default_inline_meta_json,
        ) = self.parse_data_from_md(manager_directory + "config/config.md")

        root_dirs = self.index_json_dirs(self.directory_config_json)
        # ['Courses', 'Linux Reference']
        self.templates = self.get_templates(manager_directory)

        self.output_json_file = manager_directory + "directory_index.json"

        self.configs = {
            "vault_root_directory": vault_root_directory,
            "manager_directory": manager_directory,
            "obsidian_config_dir": vault_root_directory + ".obsidian/",
            "plugins_dir": vault_root_directory + ".obsidian/plugins/",
            "config_md_file": manager_directory + "config/config.md",
            "rest-api-key": "",
            "rest-api-url": primary_config_json["rest-api-url"],
            "community-plugins-json": primary_config_json["rest-api-url"],
            "default-note-name": primary_config_json["default-note-name"],
            "root-dirs": root_dirs,
        }
        self.get_api_key()
        authorization = "Bearer " + self.configs["rest-api-key"]
        self.get_headers = {
            "accept": "application/json",
            "Authorization": authorization,
        }
        self.post_headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            "Authorization": authorization,
        }

        self.put_new_note_headers = {
            "accept": "application/json",
            "Content-Type": "text/markdown",
            "Authorization": authorization,
        }

    def get_request(self, url, headers, params):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def post_request(self, data, headers):
        try:
            url = self.configs["rest-api-url"] + data["prefix"] + data["filename"]
            data = data["content"]
            response = requests.post(url, data=data, headers=headers, verify=False)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")

    def put_request(self, data, headers):
        try:
            url = self.configs["rest-api-url"] + data["prefix"] + data["filename"]
            data = data["content"]
            response = requests.put(url, data=data, headers=headers, verify=False)
            response.raise_for_status()
            print(response.text)
        except requests.RequestException as e:
            print(f"An error occurred: {e}")

    def get_vault_path(self):
        manager_dir_raw = os.path.dirname(os.path.realpath(__file__))
        manager_dir_split = manager_dir_raw.split("/")
        manager_directory = manager_dir_raw.replace(manager_dir_split[-1], "")
        vault_root_directory = manager_directory.replace(
            manager_dir_split[-2], ""
        ).replace("//", "/")
        return manager_directory, vault_root_directory

    def parse_data_from_md(self, md_file_path):
        with open(md_file_path, "r", encoding="utf-8") as md_file:
            content = md_file.read()

        start = content.find("```json primary-config") + len("```json primary-config")
        end = content.find("primary-config```", start)
        json_str = content[start:end].strip()
        primary_config_json = json.loads(json_str)

        start = content.find("```json directory-config") + len(
            "```json directory-config"
        )
        end = content.find("directory-config```", start)
        json_str = content[start:end].strip()
        directory_config_json = json.loads(json_str)

        start = content.find("```markdown default-inline-meta") + len(
            "```markdown default-inline-meta"
        )
        end = content.find("default-inline-meta```", start)
        default_inline_meta_json = content[start:end].strip()
        return primary_config_json, directory_config_json, default_inline_meta_json

    def index_json_dirs(self, json_data):
        root_dirs = []
        for i in json_data:
            root_dirs.append(i)
        return root_dirs

    def create_dirs(self, directory_config_json, root_dirs, vault_root_dir):
        for i in root_dirs:
            os.makedirs(vault_root_dir + i, exist_ok=True)
            for dir in directory_config_json[i]["directories"]:
                os.makedirs(vault_root_dir + i + "/" + dir, exist_ok=True)
                for subdir in directory_config_json[i]["directories"][dir]:
                    os.makedirs(
                        vault_root_dir + i + "/" + dir + "/" + subdir, exist_ok=True
                    )

    def create_indexes(self, directory_config, root_dirs, vault_root, templates):
        # Ensure paths end with a slash
        vault_root = os.path.join(vault_root, "")

        # Primary Index
        primary_index_template_path = os.path.join(
            templates["templates-required"]["directory"],
            templates["templates-required"]["names"][0],
        )
        primary_index_dest_path = os.path.join(vault_root, "Index.md")
        shutil.copyfile(primary_index_template_path, primary_index_dest_path)

        # Secondary Indexes
        for root_dir in root_dirs:
            secondary_index_template_path = os.path.join(
                templates["templates-required"]["directory"],
                templates["templates-required"]["names"][1],
            )
            secondary_index_dest_path = os.path.join(vault_root, root_dir, "Index.md")
            os.makedirs(os.path.dirname(secondary_index_dest_path), exist_ok=True)
            shutil.copyfile(secondary_index_template_path, secondary_index_dest_path)

            # Tertiary Indexes (Directly within each course directory)
            if root_dir in directory_config:
                for directory in directory_config[root_dir]["directories"]:
                    tertiary_index_template_path = os.path.join(
                        templates["templates-required"]["directory"],
                        templates["templates-required"]["names"][2],
                    )
                    tertiary_index_dest_path = os.path.join(
                        vault_root, root_dir, directory, "Index.md"
                    )
                    os.makedirs(
                        os.path.dirname(tertiary_index_dest_path), exist_ok=True
                    )
                    shutil.copyfile(
                        tertiary_index_template_path, tertiary_index_dest_path
                    )

                    # For each sub-directory within each course directory
                    for subdir in directory_config[root_dir]["directories"][directory]:
                        tertiary_index_dest_subdir_path = os.path.join(
                            vault_root, root_dir, directory, subdir, "Index.md"
                        )
                        os.makedirs(
                            os.path.dirname(tertiary_index_dest_subdir_path),
                            exist_ok=True,
                        )
                        shutil.copyfile(
                            tertiary_index_template_path,
                            tertiary_index_dest_subdir_path,
                        )

    def index_directory(self):
        path = self.configs["vault_root_directory"]
        directory_index = {}
        for root, dirs, files in os.walk(path, topdown=True):

            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "Manager"]

            relative_path = os.path.relpath(root, path)
            if relative_path == ".":
                relative_path = ""

            sub_index = {}
            for d in dirs:
                sub_index[d] = {}

            filtered_files = [f for f in files if not f.startswith(".")]
            if filtered_files:
                sub_index["files"] = filtered_files

            if relative_path:
                parts = relative_path.split(os.sep)
                temp = directory_index
                for part in parts[:-1]:
                    temp = temp.get(part, {})
                temp[parts[-1]] = sub_index
            else:
                directory_index.update(sub_index)

        self.save_index_to_json(directory_index, self.output_json_file)

    def save_index_to_json(self, directory_index, output_file):
        try:
            with open(output_file, "w") as f:
                json.dump(directory_index, f, indent=4)
        except Exception as e:
            print(f"Error saving directory index to {output_file}: {e}")

    def get_api_key(self):
        plugins_dir = self.configs["plugins_dir"]
        with open(f"{plugins_dir}/obsidian-local-rest-api/data.json", "r") as file:
            data = json.load(file)
        self.configs["rest-api-key"] = data["apiKey"]

    def get_templates(self, manager_dir):
        templates = {
            "templates": {
                "directory": manager_dir + "Templates/Complete/",
                "names": [],
            },
            "templates-components": {
                "directory": manager_dir + "Templates/Components/",
                "names": [],
            },
            "templates-required": {
                "directory": manager_dir + "Templates/Required/",
                "names": [],
            },
        }

        for template_type in templates.values():
            directory_path = template_type["directory"]
            if os.path.isdir(directory_path):  # Check if the directory exists
                for filename in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, filename)
                    if os.path.isfile(
                        file_path
                    ):  # Make sure it's a file, not a directory
                        template_type["names"].append(filename)

        return templates

    def closeEvent(self, event):
        # Close all NoteCreator instances
        for noteCreator in self.noteCreatorWindows:
            noteCreator.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    mainWindow = HomeWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
