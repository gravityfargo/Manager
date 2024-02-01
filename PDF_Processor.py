import os, shutil
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QSpacerItem,
    QSizePolicy,
    QApplication,
)


class PDFProcessor(QWidget):
    def __init__(self, json_data, vault_path):
        super().__init__()
        self._load_json_data(json_data["purpose"]["PDF_Import"])
        self.vault_path = vault_path
        self.class_input = ""
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("PyPorter - Process PDF"))

        self.pick_file_to_import_button = QPushButton("Target PDF")
        self.pick_file_to_import_button.clicked.connect(
            lambda: self.pick_file_to_import()
        )
        self.layout.addWidget(self.pick_file_to_import_button)
        self._setup_type_combo()
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)
        self._setup_filename_label_input()
        self._setup_extra_inputs()

        self.confirm_button = QPushButton("Select Directory and Import")
        self.confirm_button.clicked.connect(
            lambda: self.confirm_selections()
        )
        self.layout.addWidget(self.confirm_button)

    def _load_json_data(self, edu_data):
        self.pdftypes = edu_data["type"]

    def pick_file_to_import(self):
        self.target_file_path, _ = QFileDialog.getOpenFileName(
            caption="Select PDF to Import",
            directory=self.vault_path,
            filter="PDF Files (*.pdf)",
        )
        i = self.target_file_path.split("/")
        j = len(i)
        self.target_file_name = i[j - 1]
        self.filename_label_input.setDisabled(False)
        self.class_input.setDisabled(False)
        self.filename_label_input.setText(self.target_file_name)

    def pick_save_path(self, default_filename):
        self.pdf_path, _ = QFileDialog.getSaveFileName(
            self, 
            caption="Save File", 
            directory=default_filename, 
            filter="PDF Files (*.pdf)"
        )

    def _setup_extra_inputs(self):
        self.class_input_label = QLabel("Optional Class:")
        self.class_input = QLineEdit()
        self.class_input.setDisabled(True)
        self.layout.addWidget(self.class_input_label)
        self.layout.addWidget(self.class_input)

    def _setup_filename_label_input(self):
        self.filename_label = QLabel("Name of File:")
        self.filename_label_input = QLineEdit()
        self.filename_label_input.setDisabled(True)
        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.filename_label_input)

    def _setup_type_combo(self):
        self.type_combo = QComboBox()
        self.type_combo_label = QLabel("PDF Type:")
        self.type_combo.addItem("", None)
        self.type_combo.currentIndexChanged.connect(self.updateFilenameInput)
        for item in self.pdftypes:
            self.type_combo.addItem(item, item)
        self.layout.addWidget(self.type_combo_label)
        self.layout.addWidget(self.type_combo)

    def updateFilenameInput(self):
        current_text = self.filename_label_input.text()
        current_text = current_text.replace(".pdf", "")
        new_text = current_text  # Start with the initial text

        for item in self.pdftypes:
            new_text = new_text.replace("_" + item, "")  # Replace each item in new_text

        self.filename_label_input.setText("")
        if self.type_combo.currentText() == "":
            new_text = current_text
        else:
            new_text = new_text + " " + self.type_combo.currentText()
        self.final_name = new_text.replace(" ", "_")
        self.filename_label_input.setText(self.final_name + ".pdf")

    def confirm_selections(self):
        self.updateFilenameInput()
        temp = self.vault_path + "/" + self.final_name
        self.pick_save_path(temp)
        
        i = self.pdf_path.split("/")
        j = len(i)
        fname = i[j - 1].replace("_", " ") # isolate filename
        # replace _ with " "
        fname_pdf = fname + ".pdf"
        fname_md = fname + ".md"
        targetdir = self.pdf_path.replace(i[j - 1], "") # remove the filename to have just the dir
        
        # get files in same dir to find index file
        files = [f for f in os.listdir(targetdir) if os.path.isfile(os.path.join(targetdir, f))]
        template_md = "\n%%"
        if len(files) != 0:
            for file in files:
                if "_Index.md" in file:
                    template_md += f"\nparent:: [[{file}]]"
                    index_path = targetdir + "/" + file
                    print(index_path)
                    # with open(self.template, "r", encoding="utf-8") as file:
                    #     template_md += file.read()
        else:
            template_md += "\nparent::"
            
        template_md += '\ncreated: `$= dv.current().file.ctime.toFormat("f")`'
        template_md += '\nmodified: `$= dv.current().file.mtime.toFormat("f")`'        
        template_md += f"\nannotation-target:: [[{fname_pdf}]]"
        template_md += f"\nsibling:: [[{fname_pdf}]]"
        
        template_md += f"\nclass:: {self.class_input.text()}"
        template_md += "\n%%"
        template_md += f'\n# [[{fname}]]'
        template_md += "\n`button-openannotationview`"
        
        print(fname_pdf)
        print(fname_md)
        # shutil.move(self.target_file_path, fname_pdf)
        
        # with open(fname_md, "w", encoding="utf-8") as md_file:
        #     md_file.write(template_md)
        print("Done")
        QApplication.instance().quit()
