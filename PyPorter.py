import sys, json, os
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

        self.setWindowTitle("My App")
        self.setMinimumSize(400, 600)

        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        create_note_button = QPushButton("Create Note")
        process_pdf_button = QPushButton("Process PDF")
        self.activate_tab(0)
        create_note_button.clicked.connect(lambda: self.activate_tab(1))
        process_pdf_button.pressed.connect(lambda: self.activate_tab(2))

        button_layout.addWidget(create_note_button)
        button_layout.addWidget(process_pdf_button)
        self.stacklayout.addWidget(Home())
        self.stacklayout.addWidget(
            New_Note.NoteCreator(self.json_data, self.vault_path, self.pyporter_data_directory)
        )
        self.stacklayout.addWidget(
            PDF_Processor.PDFProcessor(self.json_data, self.vault_path)
        )
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def activate_tab(self, index):
        self.stacklayout.setCurrentIndex(index)

    def initVars(self):
        self.pyporter_data_directory = "Obsidian/PyPorter/"
        self.get_vault_path()  # vault_path script_path
        self.get_json()  # json_data
        self.template_dir = self.vault_path + self.pyporter_data_directory

    def get_json(self):
        try:
            with open(
                f"{self.vault_path}{self.pyporter_data_directory}PyPorter_config.json",
                "r",
            ) as file:
                content = file.read()
            if len(content) > 0:
                self.json_data = json.loads(content)
            else:
                raise Exception("No Config")
        except Exception as e:
            print(f"An error occurred: {e}")

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