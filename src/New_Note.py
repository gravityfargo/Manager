from dataclasses import replace
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
    QApplication,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QTextEdit,
    QFileDialog    
)
from PyQt5.QtGui import QFontMetrics
from datetime import datetime
import qtawesome as qta
import os


class NoteCreator(QWidget):
    def __init__(self, configs, directory_config_json, action):
        super().__init__()
        self.action = action
        self.layout = QHBoxLayout()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.configs = configs
        self.directory_config_json = directory_config_json
        self.chosen_optional_folder_name = ""
        self.initVars()
        
        if self.action == "Create Note":
            self.setup_ui()
        elif self.action == "Import Note": 
            target_file_path, target_file_name = self.pick_file_to_import()
            self.setup_ui()
            self.populate_form(target_file_path, target_file_name)

    def initVars(self):
        self.filename_parts = {
            "root": "",
            "directory": "",
            "subfolder": "",
            "optional_subdir": "",
            "note_name": self.configs["default-note-name"]
        }

    def setup_ui(self):
        self.widget_left = QWidget()
        self.widget_left.setMinimumWidth(500)
        self.widget_right = QWidget()
        self.widget_right.setMinimumWidth(1400)

        self.layout_left = QVBoxLayout()
        self.layout_right = QVBoxLayout()

        self.layout_right_checkboxes = QVBoxLayout()
        self.layout_right_textboxes = QVBoxLayout()

        self.widget_left.setLayout(self.layout_left)
        self.widget_right.setLayout(self.layout_right)

        self.setup_root_combo()
        self.setup_directories_combo()
        self.setup_subfolder_combo()
        self.setup_optional_subdir_input()

        self.layout_right.addWidget(QLabel("Pick a template:"))

        self.layout_right.addLayout(self.layout_right_checkboxes)

        self.layout_right.addLayout(self.layout_right_textboxes)
        self.setup_checkboxes(self.configs["templates-list"])
        
        for template_path in self.configs["templates-list"]:
            self.setup_text_widgets(is_a_template="yes", template_path=template_path, contents=None, name=None)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout_left.addItem(spacer)
        self.layout_right.addItem(spacer)
        
        self.setup_filename_lineedit()

        self.create_button = QPushButton("Create Note")
        self.create_button.setDisabled(True)
        self.create_button.clicked.connect(self._on_create_button_clicked)
        self.layout_left.addWidget(self.create_button)

        self.layout.addWidget(self.widget_left)
        self.layout.addWidget(self.widget_right)

        self.setLayout(self.layout)

    def pick_file_to_import(self):
        target_file_path, _ = QFileDialog.getOpenFileName(
            caption="Select Note to Import",
            directory=self.configs["vault_root_directory"],
            filter="Markdown Files (*.md *.markdown)",
        )
        i = target_file_path.split("/")
        j = len(i)
        target_file_name = i[j - 1]
        return target_file_path, target_file_name

    def populate_form(self, path, filename):
        self.filename_parts["note_name"] = filename
        self.update_filename_lineedit()
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            
        frontmatter_start = content.find("---")
        frontmatter_end = content.find("---", frontmatter_start + len("---")) + len("---")
        if frontmatter_start != -1 and frontmatter_end != -1:
            extracted_frontmatter = content[frontmatter_start:frontmatter_end]
            content = content.replace(extracted_frontmatter, '', 1)  # Remove frontmatter from content
            self.setup_text_widgets(is_a_template="no", template_path=None, contents=extracted_frontmatter, name="extracted_frontmatter")
        
        comments_start = content.find("%%")
        comments_end = content.find("%%", comments_start + len("%%")) + len("%%")
        if comments_start != -1 and comments_end != -1:
            extracted_comments = content[comments_start:comments_end]
            content = content.replace(extracted_comments, '', 1)  # Remove comments from content
            self.setup_text_widgets(is_a_template="no", template_path=None, contents=extracted_comments, name="extracted_comments")

        self.setup_text_widgets(is_a_template="no", template_path=None, contents=content.strip(), name="extracted_content")
                    
    def populate_combo(self, widget, data):
        for item in data:
            widget.addItem(item, item)

    def setup_root_combo(self):
        self.root_combo = QComboBox()
        self.root_combo_label = QLabel("Root Folder:")
        self.root_combo.addItem("", None)
        self.populate_combo(self.root_combo, self.configs["root-dirs"])
        self.root_combo.currentIndexChanged.connect(self.root_folder_index_changed)
        self.layout_left.addWidget(self.root_combo_label)
        self.layout_left.addWidget(self.root_combo)

    def setup_directories_combo(self):
        self.directories_combo = QComboBox()
        self.directories_combo_label = QLabel("Directories:")
        self.directories_combo.addItem("", None)
        self.directories_combo.setHidden(True)
        self.directories_combo_label.setHidden(True)
        self.directories_combo.currentIndexChanged.connect(
            self.directories_combo_index_changed
        )
        self.layout_left.addWidget(self.directories_combo_label)
        self.layout_left.addWidget(self.directories_combo)

    def setup_subfolder_combo(self):
        self.subfolder_combo = QComboBox()
        self.subfolder_combo_label = QLabel("Subfolder:")
        self.subfolder_combo.addItem("", None)
        self.subfolder_combo.setHidden(True)
        self.subfolder_combo_label.setHidden(True)
        self.subfolder_combo.currentIndexChanged.connect(
            self.subfolder_combo_index_changed
        )
        self.layout_left.addWidget(self.subfolder_combo_label)
        self.layout_left.addWidget(self.subfolder_combo)

    def setup_optional_subdir_input(self):
        self.optional_subdir_label = QLabel("Optional Sub Dir:")
        self.optional_subdir_input = QLineEdit()
        self.optional_subdir_label.setHidden(True)
        self.optional_subdir_input.setHidden(True)
        self.layout_left.addWidget(self.optional_subdir_label)
        self.layout_left.addWidget(self.optional_subdir_input)
        self.optional_subdir_input.textChanged.connect(self.optional_subdir_input_text_changed)

    def setup_filename_lineedit(self):
        self.filename_lineedit_label = QLabel("Name of File:")
        self.filename_lineedit = QLineEdit()
        self.filename_lineedit.setDisabled(True)
        self.layout_right.addWidget(self.filename_lineedit_label)
        self.layout_right.addWidget(self.filename_lineedit)

    def setup_checkboxes(self, template_list):
        hbox = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(hbox)
        counter = 0 
        for i, item in enumerate(template_list):
            text = item.split("/")[-1].replace(".md", "")
            checkbox = QCheckBox(text)
            checkbox.stateChanged.connect(self.show_text_widget)
            checkbox.setObjectName(text)
            
            if text != "Default_Contents":
                hbox.addWidget(checkbox)
                counter += 1
            
            if counter == 2 or (i == len(template_list) - 1 and counter != 0):
                self.layout_right_checkboxes.addWidget(widget)
                if i != len(template_list) - 1:
                    hbox = QHBoxLayout()
                    widget = QWidget()
                    widget.setLayout(hbox)
                    counter = 0

    def setup_text_widgets(self, is_a_template, template_path, contents, name):
        if is_a_template == "yes":
            contents = ""
            with open(template_path, "r", encoding="utf-8") as file:
                contents = file.read()
            name = template_path.split("/")[-1].replace(".md", "")
            
        widget = QWidget(self)
        vbox = QVBoxLayout(widget)

        nameLabel = QLabel(name.replace("_", " ").title())
        vbox.addWidget(nameLabel)
        
        textbox = QTextEdit()
        textbox.setText(contents)
        textbox.setLineWrapMode(QTextEdit.NoWrap)
        
        textbox.document().setPlainText(contents)
        font = textbox.document().defaultFont()
        fontMetrics = QFontMetrics(font)
        textSize = fontMetrics.size(0, textbox.toPlainText())
        h = textSize.height()
        textbox.setMinimumHeight(h)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        btn_layout = QVBoxLayout()

        up_icon = qta.icon("mdi6.menu-up-outline")
        btn_up = QPushButton()
        btn_up.setIcon(up_icon)
        btn_up.clicked.connect(lambda: self.move_text_widget(widget, True))

        down_icon = qta.icon("mdi6.menu-down-outline")
        btn_down = QPushButton()
        btn_down.setIcon(down_icon)
        btn_down.clicked.connect(lambda: self.move_text_widget(widget, False))

        btn_layout.addWidget(btn_up)
        btn_layout.addWidget(btn_down)

        hbox.addWidget(textbox)
        hbox.addLayout(btn_layout)

        widget.setObjectName(name)
        if is_a_template == "yes" and self.action == "Create Note":
            if widget.objectName() == "Default_Contents":
                textbox.setPlaceholderText("Note Contents")
            else:
                widget.setHidden(True)
        elif is_a_template == "yes" and self.action == "Import Note":
            widget.setHidden(True)
            
        self.layout_right_textboxes.addWidget(widget)

    def root_folder_index_changed(self, index):
        self.chosen_root_folder = self.root_combo.currentText()
        self.filename_parts["root"] = self.chosen_root_folder
        self.update_filename_lineedit()
        self.populate_combo(
            self.directories_combo,
            self.directory_config_json[self.chosen_root_folder]["directories"],
        )
        self.directories_combo.setHidden(False)
        self.directories_combo_label.setHidden(False)
        self.filename_lineedit.setDisabled(False)

    def directories_combo_index_changed(self, index):
        chosen_directory = self.directories_combo.currentText()
        self.filename_parts["directory"] = chosen_directory
        self.update_filename_lineedit()
        self.populate_combo(
            self.subfolder_combo,
            self.directory_config_json[self.chosen_root_folder]["directories"][
                chosen_directory
            ],
        )
        self.subfolder_combo.setHidden(False)
        self.subfolder_combo_label.setHidden(False)
        self.optional_subdir_label.setHidden(False)
        self.optional_subdir_input.setHidden(False)
        self.create_button.setDisabled(False)
        
    def subfolder_combo_index_changed(self, index):
        chosen_sub_directory = self.subfolder_combo.currentText()
        self.filename_parts["subfolder"] = chosen_sub_directory
        self.update_filename_lineedit()

    def update_filename_lineedit(self):
        new_filename = ""
        for key, value in self.filename_parts.items():
            if value != "" and key == "root":
                 new_filename += value
            elif value != "":
                new_filename += f"/{value}"
        self.filename_lineedit.setText(new_filename)

    def optional_subdir_input_text_changed(self, text):
        self.filename_parts["optional_subdir"] = self.optional_subdir_input.text()
        self.update_filename_lineedit()

    def show_text_widget(self):
        checkbox = self.sender()
        for i in range(self.layout_right_textboxes.count()):
            item = self.layout_right_textboxes.itemAt(i)
            widget = item.widget()
            if widget.objectName() == checkbox.objectName():
                if widget.isHidden():
                    widget.setHidden(False)
                    self.layout_right_textboxes.insertWidget(0, widget)
                else:
                    widget.setHidden(True)

    def move_text_widget(self, widget, up):
        index = self.layout_right_textboxes.indexOf(widget)
        if up and index > 0:
            self.layout_right_textboxes.insertWidget(index - 1, widget)
        elif not up and index < self.layout_right_textboxes.count() - 1:
            self.layout_right_textboxes.insertWidget(index + 1, widget)

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
        new_file_content = ""
        for i in range(self.layout_right_textboxes.count()):
            item = self.layout_right_textboxes.itemAt(i)
            widget = item.widget()
            textEditText = widget.findChild(QTextEdit)
            new_file_content += f"{textEditText.toPlainText()}\n"
        # self.rebuildStringWithDate(sanitized_filename)
        # os.makedirs(self.dest_path, exist_ok=True)
        with open(self.filename_lineedit.text(), "w", encoding="utf-8") as md_file:
            md_file.write(new_file_content)

        self.close()
