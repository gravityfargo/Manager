import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QApplication
from PyQt5.QtCore import pyqtSignal
import shutil

class PDFProcessor(QWidget):
    data_sent = pyqtSignal(dict)

    def __init__(self, configs):
        super().__init__()
        self.configs = configs
        self.vault_path = self.configs["vault_root_dir"]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Process PDF"))
        self.pick_pdf_btn = QPushButton("Pick PDF")
        self.pick_pdf_btn.clicked.connect(self.pick_pdf)
        layout.addWidget(self.pick_pdf_btn)
        self.pdf_name_label = QLabel("No PDF selected")
        layout.addWidget(self.pdf_name_label)
        self.confirm_btn = QPushButton("Process and Save PDF")
        self.confirm_btn.clicked.connect(self.process_pdf)
        layout.addWidget(self.confirm_btn)

    def pick_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", self.vault_path, "PDF Files (*.pdf)")
        if file_path:
            self.selected_pdf = file_path
            self.pdf_name_label.setText(os.path.basename(file_path))

    def process_pdf(self):
        if hasattr(self, "selected_pdf"):
            target_dir = QFileDialog.getExistingDirectory(self, "Select Target Directory", self.vault_path)
            if target_dir:
                try:
                    base_name = os.path.basename(self.selected_pdf)
                    new_pdf_path = os.path.join(target_dir, base_name)
                    md_file_path = os.path.splitext(new_pdf_path)[0] + ".md"
                    shutil.move(self.selected_pdf, new_pdf_path)
                    with open(md_file_path, "w") as md_file:
                        md_file.write(f'---\nannotation-target: "[[{base_name}]]"\n---\n')
                    print("PDF processed and MD file created successfully.")
                except Exception as e:
                    print(f"Error processing PDF: {e}")
        else:
            print("No PDF selected")