import sys, json, os, requests
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QApplication,
    QMainWindow,
    QStackedLayout,
    QHBoxLayout,
)
import PDF_Processor, New_Note


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initVars()
        self.files_setup()
        
        # response_data = self.get_request(self.base_settings["rest-api-url"], headers=self.get_headers, params=None)
        # print(response_data)
            

    # self.setWindowTitle("My App")
    # self.setMinimumSize(400, 600)

    # pagelayout = QVBoxLayout()
    # button_layout = QHBoxLayout()
    # self.stacklayout = QStackedLayout()

    # pagelayout.addLayout(button_layout)
    # pagelayout.addLayout(self.stacklayout)

    # create_note_button = QPushButton("Create Note")
    # process_pdf_button = QPushButton("Process PDF")
    # self.activate_tab(0)
    # create_note_button.clicked.connect(lambda: self.activate_tab(1))
    # process_pdf_button.pressed.connect(lambda: self.activate_tab(2))

    # button_layout.addWidget(create_note_button)
    # button_layout.addWidget(process_pdf_button)
    # self.stacklayout.addWidget(Home())
    # self.stacklayout.addWidget(
    #     New_Note.NoteCreator(self.json_data, self.vault_path, self.pyporter_data_directory)
    # )
    # self.stacklayout.addWidget(
    #     PDF_Processor.PDFProcessor(self.json_data, self.vault_path)
    # )
    # widget = QWidget()
    # widget.setLayout(pagelayout)
    # self.setCentralWidget(widget)
    
    def initVars(self):
        self.get_vault_path()  # self.vault_path, self.script_path
        self.program_dir = self.script_path.replace("/src", "")  # .obsidian/scripts/python/Python-Obsidian-Manager
        self.configuration_md = self.program_dir + "/config/config.md"
        self.parse_json_from_md(self.configuration_md) # self.json_data
        
        self.base_settings = self.json_data["base-settings"]
        self.vault_visible_dir = self.vault_path + "/" + self.base_settings["vault-visible-dir"]
        self.get_headers = headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer 06ea7e98a1ef3157e10908f3715ce178a8baf02bf39b62b0b83e2561a6ada94e'
        }
        self.post_headers = {'Content-Type': 'application/json'}
     
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
        script_directory = os.path.dirname(os.path.realpath(__file__))
        vault_path = ""
        for dir in script_directory.split("/"):
            if dir != ".obsidian":
                vault_path = vault_path + f"/{dir}"
            else:
                break
        self.vault_path = vault_path.replace("//", "/") + "/"
        self.script_path = script_directory.replace(vault_path, "")

    def parse_json_from_md(self, md_file_path):
        with open(md_file_path, "r", encoding="utf-8") as md_file:
            content = md_file.read()
        start = content.find("```json") + len("```json")
        end = content.find("```", start)
        json_str = content[start:end].strip()
        self.json_data = json.loads(json_str)

    def files_setup(self):
        os.makedirs(self.vault_visible_dir, exist_ok=True)
        entries = os.listdir(self.program_dir)
        for entry in entries:
            if not entry.startswith("."):

                source = self.program_dir + "/" + entry
                symlink_path = self.vault_visible_dir + "/" + entry

                if not os.path.islink(symlink_path):
                    # Create the symlink if it doesn't exist
                    os.symlink(source, symlink_path)
                    print(f"Symlink created: {symlink_path} -> {source}")
                else:
                    print("Symlink already exists.")

    def activate_tab(self, index):
        self.stacklayout.setCurrentIndex(index)


class Home(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Click a button."))
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
