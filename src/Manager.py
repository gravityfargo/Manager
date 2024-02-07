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
import PDF_Processor, Note_Processor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.note_windows = []
        self.init_vars()
        self.setup_ui()
        self.index_directory()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        create_btn = QPushButton("Create Note")
        create_btn.clicked.connect(self.create_note)
        layout.addWidget(create_btn)

        import_btn = QPushButton("Import Note")
        import_btn.clicked.connect(self.import_note)
        layout.addWidget(import_btn)

        process_pdf_btn = QPushButton("Process PDF")
        process_pdf_btn.clicked.connect(self.import_pdf)
        layout.addWidget(process_pdf_btn)

    def create_note(self):
        creator = Note_Processor.Note_Processor(
            self.configs, self.dir_config_json, self.templates, "Create Note"
        )
        creator.data_sent.connect(self.handle_data)
        creator.show()
        self.note_windows.append(creator)

    def handle_data(self, data):
        if data["type"] == "new_note":
            data["prefix"] = "/vault"
            self.put_request(data, self.put_new_note_headers)
            data["prefix"] = "/open"
            data["content"] = ""
            self.post_request(data, self.post_headers)

    def import_note(self):
        importer = Note_Processor.Note_Processor(
            self.configs, self.dir_config_json, self.templates, "Import Note"
        )
        importer.data_sent.connect(self.handle_data)
        importer.show()
        self.note_windows.append(importer)

    def import_pdf(self):
        pdf_importer = PDF_Processor.PDFProcessor(self.configs)
        pdf_importer.data_sent.connect(self.handle_data)
        pdf_importer.show()
        self.note_windows.append(pdf_importer)

    def init_vars(self):
        manager_dir, vault_root_dir = self.get_vault_path()
        config_json, self.dir_config_json = self.parse_data_from_md(manager_dir + "config/config.md")
        root_dirs = self.index_json_dirs(self.dir_config_json)
        self.templates = self.get_templates(manager_dir)

        self.create_dirs(self.dir_config_json, root_dirs, vault_root_dir)
        self.create_indexes(self.dir_config_json, root_dirs, vault_root_dir, self.templates)

        self.output_json_file = manager_dir + "directory_index.json"

        self.configs = {
            "vault_root_dir": vault_root_dir,
            "manager_dir": manager_dir,
            "obsidian_config_dir": vault_root_dir + ".obsidian/",
            "plugins_dir": vault_root_dir + ".obsidian/plugins/",
            "config_md_file": manager_dir + "config/config.md",
            "rest-api-key": "",
            "rest-api-url": config_json["rest-api-url"],
            "community-plugins-json": config_json["rest-api-url"],
            "default-note-name": config_json["default-note-name"],
            "root-dirs": root_dirs,
        }
        self.get_api_key()
        authorization = "Bearer " + self.configs["rest-api-key"]
        self.auth_headers = {
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

    def put_request(self, data, headers=None):
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
        manager_dir = manager_dir_raw.replace(manager_dir_split[-1], "")
        vault_root_dir = manager_dir.replace(
            manager_dir_split[-2], ""
        ).replace("//", "/")
        return manager_dir, vault_root_dir

    def parse_data_from_md(self, md_file_path):
        with open(md_file_path, "r", encoding="utf-8") as md_file:
            content = md_file.read()

        start = content.find("```json primary-config") + len("```json primary-config")
        end = content.find("primary-config```", start)
        json_str = content[start:end].strip()
        config_json = json.loads(json_str)

        start = content.find("```json directory-config") + len(
            "```json directory-config"
        )
        end = content.find("directory-config```", start)
        json_str = content[start:end].strip()
        directory_config_json = json.loads(json_str)

        return config_json, directory_config_json

    def index_json_dirs(self, json_data):
        root_dirs = []
        for i in json_data:
            root_dirs.append(i)
        return root_dirs

    def create_dirs(self, dir_config_json, root_dirs, vault_root_dir):
        for i in root_dirs:
            os.makedirs(vault_root_dir + i, exist_ok=True)
            for dir in dir_config_json[i]["directories"]:
                os.makedirs(vault_root_dir + i + "/" + dir, exist_ok=True)
                for subdir in dir_config_json[i]["directories"][dir]:
                    os.makedirs(
                        vault_root_dir + i + "/" + dir + "/" + subdir, exist_ok=True
                    )

    def create_indexes(self, directory_config, root_dirs, vault_root, templates):
        vault_root = os.path.join(vault_root, "")

        primary_index_template_path = os.path.join(
            templates["templates-required"]["directory"],
            templates["templates-required"]["names"][0],
        )
        primary_index_dest_path = os.path.join(vault_root, "Index.md")
        shutil.copyfile(primary_index_template_path, primary_index_dest_path)

        for root_dir in root_dirs:
            secondary_index_template_path = os.path.join(
                templates["templates-required"]["directory"],
                templates["templates-required"]["names"][1],
            )
            secondary_index_dest_path = os.path.join(vault_root, root_dir, "Index.md")
            os.makedirs(os.path.dirname(secondary_index_dest_path), exist_ok=True)
            shutil.copyfile(secondary_index_template_path, secondary_index_dest_path)

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
        path = self.configs["vault_root_dir"]
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
            if os.path.isdir(directory_path):
                for filename in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, filename)
                    if os.path.isfile(
                        file_path
                    ):
                        template_type["names"].append(filename)

        return templates

    def closeEvent(self, event):
        for window in self.note_windows:
            window.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
