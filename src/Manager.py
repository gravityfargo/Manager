import sys, json, os, requests
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QApplication,
    QMainWindow
)
import PDF_Processor, New_Note

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.noteCreatorWindows = []
        self.initVars()
        self.create_dirs(self.directory_config_json, self.configs["root-dirs"], self.configs["vault_root_directory"])
        self.setWindowTitle("Obsidian Manager")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.setupUI()
        
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
        noteCreator = New_Note.NoteCreator(self.configs, self.directory_config_json, "Create Note")
        noteCreator.dataSent.connect(self.handleNoteCreatorData)  # Connect signal to slot
        noteCreator.show()
        self.noteCreatorWindows.append(noteCreator)

    def handleNoteCreatorData(self, data):
        print("Data received from NoteCreator:", data)

    def launchImportNote(self):
        self.noteImporter = New_Note.NoteCreator(self.configs, self.directory_config_json, "Import Note")
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
        templates_list = []
        templates_components_list = []
        for template in primary_config_json["templates-list"]:
            templates_list.append(manager_directory + "Templates/" + template + ".md")
        for template in primary_config_json["templates-components-list"]:
            templates_components_list.append(manager_directory + "Templates/" + template + ".md")
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
            "templates-list": templates_list,
            "templates-components-list": templates_components_list,
            "root-dirs": root_dirs,
        }
        self.get_api_key(self.configs["plugins_dir"])
        authorization = "Bearer " + self.configs["rest-api-key"]
        self.get_headers = {
            "accept": "application/json",
            "Authorization": authorization,
        }
        self.post_headers = {"Content-Type": "application/json"}
        
        self.put_new_note_headers = {
            "accept": "application/json",
            "Content-Type": "text/markdown"
        }

    def get_request(self, url, headers=None, params=None):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def post_request(self, url, data, headers=None):
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()  # Assuming response is in JSON format
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

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

    def get_api_key(self, plugins_dir):
        with open(f"{plugins_dir}/obsidian-local-rest-api/data.json", "r") as file:
            data = json.load(file)
        self.configs["rest-api-key"] = data["apiKey"]

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
