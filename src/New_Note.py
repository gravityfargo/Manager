from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
    QApplication
)
from datetime import datetime
import os


class NoteCreator(QWidget):
    DEFAULT_NOTE_NAME = "New_Note"
    FILE_EXTENSION = ".md"

    def __init__(self, json_data, vault_path, pyporter_data_directory):
        super().__init__()

        self._load_json_data(json_data["purpose"]["education"])
        self.vault_path = vault_path
        self.pyporter_data_directory = pyporter_data_directory
        self.current_date = datetime.now().strftime("%Y_%m_%d")
        self.new_note_name = self.DEFAULT_NOTE_NAME
        self.chosen_optional_folder_name = ""

        self._initialize_staging_path_dict()
        self._setup_ui()

    def _load_json_data(self, edu_data):
        self.root_course_folder = edu_data["root_course_folder"].replace("/", "")
        self.folder_names = edu_data["folder_names"]
        self.course_names = edu_data["course_names"]
        self.front_matter = edu_data["front_matter"]
        self.inline_metadata = edu_data["inline_metadata"]
        self.template_file_name = edu_data["default_template"]

    def _initialize_staging_path_dict(self):
        self.staging_path_dict = {
            "root": {"index": 0, "text": self.root_course_folder},
            "course_name": {"index": 1, "text": ""},
            "folder_name": {"index": 2, "text": ""},
            "optional_subdir": {"index": 3, "text": ""},
            "filename": {"index": 4, "text": ""},
            "suffix": {"index": 5, "text": ""},
        }

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("PyPorter - Education New Note"))

        self._setup_course_combo()
        self._setup_subfolder_combo()
        self._setup_optional_subdir_input()
        self._setup_checkboxes()
        self._setup_suffix_combo()
        self._setup_filename_label_input()

        self.working_path = QLabel(self.root_course_folder)
        self.create_button = QPushButton("Create Note")
        self.create_button.clicked.connect(self._on_create_button_clicked)

        self.layout.addWidget(self.working_path)
        self.layout.addWidget(self.create_button)

    def populate_combo(self, widget, data):
        for item in data:
            widget.addItem(item, item)

    def _setup_course_combo(self):
        self.course_combo = QComboBox()
        self.course_combo_label = QLabel("Course:")
        self.course_combo.addItem("Select an option", None)
        self.populate_combo(self.course_combo, self.course_names)
        self.course_combo.currentIndexChanged.connect(self.courseComboIndexChanged)
        self.layout.addWidget(self.course_combo_label)
        self.layout.addWidget(self.course_combo)

    def _setup_subfolder_combo(self):
        self.subfolder_combo = QComboBox()
        self.subfolder_combo_label = QLabel("Subfolder:")
        self.subfolder_combo.addItem("Select an option", None)
        self.populate_combo(self.subfolder_combo, self.folder_names.keys())
        self.subfolder_combo.setDisabled(True)
        self.subfolder_combo.currentIndexChanged.connect(
            self.subfolderComboIndexChanged
        )
        self.layout.addWidget(self.subfolder_combo_label)
        self.layout.addWidget(self.subfolder_combo)

    def _setup_optional_subdir_input(self):
        self.optional_subdir_label = QLabel("Optional Sub Dir:")
        self.optional_subdir_input = QLineEdit()
        self.optional_subdir_input.setDisabled(True)
        self.optional_subdir_input.textChanged.connect(
            self.optionalSubdirInputTextChanged
        )
        self.layout.addWidget(self.optional_subdir_label)
        self.layout.addWidget(self.optional_subdir_input)

    def _setup_checkboxes(self):
        self.date_checkbox = QCheckBox(self.current_date)
        self.date_checkbox.stateChanged.connect(self.updateFilenameEditbox)
        self.class_checkbox = QCheckBox()
        self.class_checkbox.stateChanged.connect(self.updateFilenameEditbox)
        self.date_checkbox.setDisabled(True)
        self.class_checkbox.setDisabled(True)
        self.layout.addWidget(self.date_checkbox)
        self.layout.addWidget(self.class_checkbox)

    def _setup_suffix_combo(self):
        self.suffix_combo = QComboBox()
        self.suffix_combo_label = QLabel("Suffix:")
        self.suffix_combo.addItem("Select an option", None)
        self.suffix_combo.setDisabled(True)
        self.suffix_combo.currentIndexChanged.connect(self.suffixComboIndexChanged)
        self.layout.addWidget(self.suffix_combo_label)
        self.layout.addWidget(self.suffix_combo)

    def _setup_filename_label_input(self):
        self.filename_label = QLabel("Name of File:")
        self.filename_label_input = QLineEdit()
        self.filename_label_input.setPlaceholderText(self.new_note_name)
        self.filename_label_input.setDisabled(True)
        self.filename_label_input.textChanged.connect(self.filenameInputTextChanged)
        self.layout.addWidget(self.filename_label)
        self.layout.addWidget(self.filename_label_input)

    def courseComboIndexChanged(self, index):
        self.chosen_coursename = self.course_combo.currentText()
        self.updatePathLabel("course_name", self.chosen_coursename)
        self.subfolder_combo.setDisabled(False)
        self.optional_subdir_input.setDisabled(False)
        self.class_checkbox.setText(self.chosen_coursename)
        self.date_checkbox.setDisabled(False)
        self.class_checkbox.setDisabled(False)
        self.suffix_combo.setDisabled(False)
        self.filename_label_input.setDisabled(False)

    def subfolderComboIndexChanged(self, index):
        self.chosen_folder_name = self.subfolder_combo.currentText()
        self.updatePathLabel("folder_name", self.chosen_folder_name)
        self.populate_combo(
            self.suffix_combo, self.folder_names[self.chosen_folder_name]["subname"]
        )

    def optionalSubdirInputTextChanged(self, text):
        self.chosen_optional_folder_name = text
        self.updatePathLabel("optional_subdir", text)

    def suffixComboIndexChanged(self, index):
        self.updatePathLabel("suffix", self.suffix_combo.currentText())
        self.updateFilenameEditbox(None)

    def updateFilenameEditbox(self, _):
        filename_parts = []
        if self.date_checkbox.isChecked():
            filename_parts.append(self.current_date)
        if self.class_checkbox.isChecked() and self.chosen_coursename:
            filename_parts.append(self.chosen_coursename)
        selected_suffix = self.suffix_combo.currentText()
        if selected_suffix and selected_suffix != "Select an option":
            filename_parts.append(selected_suffix)
        new_filename = "_".join(filename_parts)
        self.filename_label_input.setText(new_filename)
        self.chosen_filename = new_filename

    def filenameInputTextChanged(self, text):
        self.chosen_filename = text
        self.updatePathLabel("filename", text)

    def updatePathLabel(self, key, string):
        self.staging_path_dict[key]["text"] = string
        if key == "optional_subdir" or key == "filename":
            self.staging_path_dict[key]["text"] = string.replace(" ", "_")

        prepath = ""
        for i in self.staging_path_dict.values():
            if i["index"] == 0:
                prepath = prepath + self.staging_path_dict["root"]["text"]
            elif i["index"] == 1:
                if len(i["text"]) != 0 and i["text"] != "None":
                    prepath = prepath + "/" + i["text"]
            elif i["index"] == 2:
                if len(i["text"]) != 0 and i["text"] != "None":
                    prepath = prepath + "/" + i["text"]
            elif i["index"] == 3:
                if len(i["text"]) != 0 and i["text"] != "None":
                    prepath = prepath + "/" + i["text"]
            elif i["index"] == 4:
                # if filename
                if len(i["text"]) == 0 or i["text"] == "None":
                    # if filename empty
                    prepath = prepath + "/" + self.new_note_name
                else:
                    prepath = prepath + "/" + i["text"]
            elif i["index"] == 5:
                # append _suffix
                if len(i["text"]) != 0 and i["text"] != "None":
                    prepath = prepath + "_" + i["text"]

        chosen_final_path = prepath + ".md"
        self.working_path.setText(chosen_final_path)

    def rebuildStringWithDate(self, file_name_list):
        file_name_list = file_name_list.split("_")
        new_string_parts = []
        year, month, day = None, None, None
        for element in file_name_list:
            if len(element) == 4 and element.isdigit() and year is None:
                year = element
            elif len(element) == 2 and element.isdigit() and month is None:
                month = element
            elif len(element) == 2 and element.isdigit() and day is None:
                day = element
            else:
                new_string_parts.append(element)

        if year and month and day:
            date_string = f"{year}/{month}/{day}"
            new_string_parts.insert(0, date_string)
        new_string = " ".join(new_string_parts)

        self.rebuilt_header_string = new_string

    def _on_create_button_clicked(self):
        sanitized_filename = self.chosen_filename.replace(" ", "_")
        course_folder = f"{self.root_course_folder}/{self.chosen_coursename}"
        if len(self.chosen_optional_folder_name) != 0:
            self.dest_path = f"{course_folder}/{self.chosen_folder_name}/{self.chosen_optional_folder_name}"
        else:
            self.dest_path = f"{course_folder}/{self.chosen_folder_name}"
        final_path = f"{self.dest_path}/{sanitized_filename}.md"
        self.rebuildStringWithDate(sanitized_filename)

        os.makedirs(self.dest_path, exist_ok=True)
        #
        # frontmatter
        #
        frontmatter_md = "---"
        for prop, val in self.front_matter.items():
            frontmatter_md += f"\n{prop}: {val}"
        frontmatter_md += "\n---\n"
        #
        # inline metadata
        #
        inline_meta_md = "\n\n\n%%"
        inline_meta_md += f"\nclass: {self.chosen_coursename}"
        for prop, val in self.inline_metadata.items():
            if prop == "parents":
                inline_meta_md += f"\n{prop}:: [[{self.chosen_coursename}_Index]]"
            elif len(val) == 0:
                inline_meta_md += f"\n{prop}: {val}"
            else:
                inline_meta_md += f"\n{prop}:: {val}"
        inline_meta_md += "\n%%\n"
        #
        # template
        #
        template_md = f"# [[{self.chosen_filename}|{self.rebuilt_header_string}]]"
        with open(self.template, "r", encoding="utf-8") as file:
            template_md += file.read()

        with open(final_path, "w", encoding="utf-8") as md_file:
            md_file.write(frontmatter_md)
            md_file.write(template_md)
            md_file.write(inline_meta_md)
            
        self.close()
        QApplication.instance().quit()

