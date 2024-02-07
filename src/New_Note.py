from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QTextEdit,
    QFileDialog,
    QGroupBox,
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
import qtawesome as qta
import os


class NoteCreator(QWidget):
    dataSent = pyqtSignal(dict)

    def __init__(self, configs, directory_config_json, templates, action):
        super().__init__()
        self.subprocesses = []  # Initialize a list to track child processes
        self.action = action
        self.templates = templates
        self.layout = QHBoxLayout()
        self.current_date = f"{datetime.now().strftime('%Y-%m-%d')} "
        self.configs = configs
        self.directory_config_json = directory_config_json
        self.chosen_optional_folder_name = ""
        self.initVars()

        if self.action == "Create Note":
            self.setup_ui()
        elif self.action == "Import Note":
            self.setup_ui()
            target_file_path, target_file_name = self.pick_file_to_import()
            self.populate_form(target_file_path, target_file_name)

    def initVars(self):
        self.notename_parts = {
            "date": "",
            "note_name": self.configs["default-note-name"].replace(".md", ""),
        }
        self.filename_parts = {
            "root": "",
            "directory": "",
            "subfolder": "",
            "optional_subdir": "",
            "note_name": self.notename_parts["note_name"],
        }

    def setup_ui(self):
        self.setup_widgets_and_layouts()
        self.setup_root_combo()
        self.setup_directories_combo()
        self.setup_subfolder_combo()
        self.setup_optional_subdir_lineedit()

        self.layout_right.addLayout(self.layout_right_textboxes)
        self.setup_template_checkboxes("templates", "Complete Templates")
        self.setup_template_checkboxes("templates-components", "Component Templates")
        self.layout_center.addWidget(self.widget_macros)
        
        self.setup_template_text_widgets()
            
        self.setup_text_widgets(is_a_template="no", template_path=None, contents="", name="parsed-properties")

        self.layout_left.addItem(self.spacer)
        self.layout_right.addItem(self.spacer)

        self.setup_filename_macro_checkboxes()

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red")
        self.layout_right.addWidget(self.warning_label)

        self.setup_filename_lineedit()

        self.final_path_label = QLabel("")
        self.layout_right.addWidget(self.final_path_label)

        self.create_button = QPushButton("Create Note")
        self.create_button.setDisabled(True)
        self.create_button.clicked.connect(self.on_create_button_clicked)
        self.layout_left.addWidget(self.create_button)

        self.layout.addWidget(self.widget_left)
        self.layout.addWidget(self.widget_center)
        self.layout.addWidget(self.widget_right)
        self.widget_center.setDisabled(True)

        self.setLayout(self.layout)

    def setup_widgets_and_layouts(self):
        self.widget_left = QWidget()
        self.widget_left.setMinimumWidth(500)
        self.layout_left = QVBoxLayout()
        self.widget_left.setLayout(self.layout_left)

        self.widget_center = QWidget()
        self.widget_center.setMinimumWidth(200)
        self.layout_center = QVBoxLayout()
        self.widget_center.setLayout(self.layout_center)

        self.widget_right = QWidget()
        self.widget_right.setMinimumWidth(700)
        self.widget_right.setMinimumHeight(800)
        self.layout_right = QVBoxLayout()
        self.widget_right.setLayout(self.layout_right)

        self.layout_right_textboxes = QVBoxLayout()

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        
        self.widget_macros = QGroupBox("Filename Macros")
        self.layout_macros = QVBoxLayout()
        self.widget_macros.setLayout(self.layout_macros)
        self.widget_macros.setStyleSheet(
            "QGroupBox {"
            "border: 2px solid #404040;"
            "border-radius: 5px;"
            "margin-top: 1ex;"
            "} "
            "QGroupBox::title {"
            "subcontrol-origin: margin;"
            "left: 10px;"
            "padding: 0 3px 0 3px;"
            "}"
        )

    def update_properties(self):
        content = ""
        properties_keys = []
        properties_values = []
        # {'root': 'Courses', 'directory': 'ECE214', 'subfolder': 'Course Resources', 'optional_subdir': '', 'note_name': '2024-02-05_Raw_Note'}
        for key, value in self.directory_config_json[self.filename_parts["root"]]["naming"].items():
            properties_keys.append(key)
            properties_keys.append(value)
            
        for value in self.filename_parts.values():
            properties_values.append(value)
        
        properties_values.pop(4)
        properties_values.pop(3)
        properties_values.pop(0)
        properties_keys.append("created ")
        properties_keys.append("modified")
        properties_values.append('$= `dv.current().file.ctime.toFormat("f")`')
        properties_values.append('`$= dv.current().file.mtime.toFormat("f")`')
        properties_dict = dict(zip(properties_keys, properties_values))
            
        content += "%%\n"
        for key, value in properties_dict.items():
            if key != "note_name":
                content += f"{key}:: {value}\n"
        content += "%%\n"

        widget = self.find_text_widget("parsed-properties")
        if widget:
            # Find the QTextEdit within the QWidget
            textEdit = widget.findChild(QTextEdit)
            if textEdit:
                textEdit.setText(content)
                widget.setVisible(True)  # Make sure the container QWidget is visible
            else:
                print("QTextEdit not found inside QWidget")
        else:
            print("QWidget not found")
        
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
        self.notename_parts["note_name"] = filename
        self.triggered_final_path_label_edited()
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        frontmatter_start = content.find("---")
        frontmatter_end = content.find("---", frontmatter_start + len("---")) + len(
            "---"
        )
        if frontmatter_start != -1 and frontmatter_end != -1:
            extracted_frontmatter = content[frontmatter_start:frontmatter_end]
            content = content.replace(
                extracted_frontmatter, "", 1
            )  # Remove frontmatter from content
            self.setup_text_widgets(
                is_a_template="no",
                template_path=None,
                contents=extracted_frontmatter,
                name="extracted_frontmatter",
            )

        comments_start = content.find("%%")
        comments_end = content.find("%%", comments_start + len("%%")) + len("%%")
        if comments_start != -1 and comments_end != -1:
            extracted_comments = content[comments_start:comments_end]
            content = content.replace(
                extracted_comments, "", 1
            )  # Remove comments from content
            self.setup_text_widgets(
                is_a_template="no",
                template_path=None,
                contents=extracted_comments,
                name="extracted_comments",
            )

        self.setup_text_widgets(
            is_a_template="no",
            template_path=None,
            contents=content,
            name="extracted_content",
        )
        frontmatter_widget = self.find_text_widget("extracted_frontmatter")
        comment_widget = self.find_text_widget("extracted_comments")
        content_widget = self.find_text_widget("extracted_content")
        # print(f"Content Widget: {content_widget.objectName()}")
        self.triggered_text_widget_visibility_toggle(frontmatter_widget)
        self.triggered_text_widget_visibility_toggle(comment_widget)
        self.triggered_text_widget_visibility_toggle(content_widget)
        
    def populate_combo(self, widget, data):
        for item in data:
            widget.addItem(item, item)

    def setup_root_combo(self):
        self.root_combo = QComboBox()
        self.root_combo_label = QLabel("Root Folder:")
        self.root_combo.addItem("", None)
        self.populate_combo(self.root_combo, self.configs["root-dirs"])
        self.root_combo.currentIndexChanged.connect(
            self.triggered_root_folder_index_changed
        )
        self.layout_left.addWidget(self.root_combo_label)
        self.layout_left.addWidget(self.root_combo)

    def setup_directories_combo(self):
        self.directories_combo = QComboBox()
        self.directories_combo_label = QLabel("Directories:")
        self.directories_combo.addItem("", None)
        self.directories_combo.setHidden(True)
        self.directories_combo_label.setHidden(True)
        self.directories_combo.currentIndexChanged.connect(
            self.triggered_directories_combo_index_changed
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
            self.triggered_subfolder_combo_index_changed
        )
        self.layout_left.addWidget(self.subfolder_combo_label)
        self.layout_left.addWidget(self.subfolder_combo)

    def setup_optional_subdir_lineedit(self):
        self.optional_subdir_label = QLabel("Optional Sub Dir:")
        self.optional_subdir_input = QLineEdit()
        self.optional_subdir_label.setHidden(True)
        self.optional_subdir_input.setHidden(True)
        self.layout_left.addWidget(self.optional_subdir_label)
        self.layout_left.addWidget(self.optional_subdir_input)
        self.optional_subdir_input.textChanged.connect(
            self.triggered_optional_subdir_input_text_changed
        )

    def setup_filename_macro_checkboxes(self):
        self.checkbox_date = QCheckBox("Current Date")
        self.checkbox_date.stateChanged.connect(
            self.triggered_filename_macro_checkboxes
        )
        self.layout_macros.addWidget(self.checkbox_date)

    def setup_filename_lineedit(self):
        filename_hbox = QHBoxLayout()
        self.filename_lineedit_label = QLabel("Name of File:")
        self.filename_lineedit = QLineEdit()
        self.filename_lineedit.setDisabled(True)
        self.layout_right.addWidget(self.filename_lineedit_label)
        filename_hbox.addWidget(self.filename_lineedit)
        filename_hbox.addWidget(QLabel(".md"))
        self.layout_right.addLayout(filename_hbox)
        self.filename_lineedit.setText(self.filename_parts["note_name"])
        self.filename_lineedit.textChanged.connect(
            self.triggered_filename_lineedit_edited
        )

    def setup_template_checkboxes(self, template_key, label):
        layout = QVBoxLayout()
        group_box = QGroupBox(label)
        group_box.setLayout(layout)
        group_box.setStyleSheet(
            "QGroupBox {"
            "border: 2px solid #404040;"
            "border-radius: 5px;"
            "margin-top: 1ex;"
            "} "
            "QGroupBox::title {"
            "subcontrol-origin: margin;"
            "left: 10px;"
            "padding: 0 3px 0 3px;"
            "}"
        )
        self.layout_center.addWidget(group_box)

        for template_name in self.templates[template_key]["names"]:
            template_name = template_name.replace(".md", "")
            checkbox = QCheckBox(template_name.replace("_", " ").title())
            checkbox.stateChanged.connect(lambda checked, name=template_name: self.triggered_text_widget_visibility_toggle(checkbox))
            checkbox.setObjectName(template_name)
            layout.addWidget(checkbox)
        layout.addItem(self.spacer)

    def setup_text_widgets(self, is_a_template, template_path, contents, name):
        if is_a_template == "yes":
            contents = ""
            with open(template_path, "r", encoding="utf-8") as file:
                contents = file.read()

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
        widget.setHidden(True)

        self.layout_right_textboxes.addWidget(widget)

    def setup_template_text_widgets(self):
        for template_category in self.templates.values():
            for template_name in template_category["names"]:
                template_path = os.path.join(template_category["directory"], template_name)
                self.setup_text_widgets(
                    is_a_template="yes",
                    template_path=template_path,
                    contents=None,
                    name=template_name.replace(".md", ""),
                )

    def triggered_root_folder_index_changed(self, index):
        self.chosen_root_folder = self.root_combo.currentText()
        self.filename_parts["root"] = self.chosen_root_folder
        self.triggered_final_path_label_edited()
        self.populate_combo(
            self.directories_combo,
            self.directory_config_json[self.chosen_root_folder]["directories"],
        )
        self.directories_combo.setHidden(False)
        self.directories_combo_label.setHidden(False)
        self.filename_lineedit.setDisabled(False)
        self.widget_center.setDisabled(False)

    def triggered_directories_combo_index_changed(self, index):
        chosen_directory = self.directories_combo.currentText()
        self.filename_parts["directory"] = chosen_directory
        self.triggered_final_path_label_edited()
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

        # Update properties content and visibility directly
        self.update_properties()

    def triggered_subfolder_combo_index_changed(self, index):
        chosen_sub_directory = self.subfolder_combo.currentText()
        self.filename_parts["subfolder"] = chosen_sub_directory
        self.triggered_final_path_label_edited()

    def triggered_filename_lineedit_edited(self):
        sender = self.sender()
        sender_text = sender.text()
        self.notename_parts["note_name"] = sender_text
        self.parse_name_string()
        self.triggered_final_path_label_edited()

    def parse_name_string(self):
        temp_str = ""
        for key, item in self.notename_parts.items():
            if item != "":
                temp_str += item
        self.filename_parts["note_name"] = ""
        self.filename_parts["note_name"] = temp_str.replace(" ", "_").replace(".md", "")

    def triggered_final_path_label_edited(self):
        new_filename = ""
        for key, value in self.filename_parts.items():
            if value != "" and key == "root":
                new_filename += value
            elif value != "":
                new_filename += f"/{value}"
        self.final_path_label.setText(new_filename.replace(" ", "_") + ".md")

        if os.path.isfile(new_filename.replace(" ", "_") + ".md"):
            self.warning_label.setText("Warning! File exists!")
        else:
            self.warning_label.setText("")
        if self.action == "Create Note":
            self.update_properties()

    def triggered_optional_subdir_input_text_changed(self, text):
        self.filename_parts["optional_subdir"] = self.optional_subdir_input.text()
        self.triggered_final_path_label_edited()

    def triggered_filename_macro_checkboxes(self):
        print("\n")
        if self.checkbox_date.isChecked():
            self.notename_parts["date"] = self.current_date
            print("Checked")
        else:
            self.notename_parts["date"] = ""
            print("Unchecked")
        
        self.filename_lineedit.textChanged.disconnect(self.triggered_filename_lineedit_edited)

        self.parse_name_string()
        self.filename_lineedit.setText(self.filename_parts["note_name"])

        self.triggered_final_path_label_edited()
        self.filename_lineedit.textChanged.connect(self.triggered_filename_lineedit_edited)

        print(f"notename: {self.notename_parts['note_name']}")
        print(f"filename: {self.filename_parts['note_name']}")
        print(f"lineedit: {self.filename_lineedit.text()}")
        print(f"label: {self.final_path_label.text()}")

    def find_text_widget(self, widget_name):
        # print(f"self.layout_right_textboxes.count(): {self.layout_right_textboxes.count()}")
        for i in range(self.layout_right_textboxes.count()):
            item = self.layout_right_textboxes.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    if widget.objectName() == widget_name:
                        return widget
        print(f"Widget {widget_name} not found")
        return None

    def move_text_widget(self, widget, up):
        index = self.layout_right_textboxes.indexOf(widget)
        if up and index > 0:
            self.layout_right_textboxes.insertWidget(index - 1, widget)
        elif not up and index < self.layout_right_textboxes.count() - 1:
            self.layout_right_textboxes.insertWidget(index + 1, widget)

    def triggered_text_widget_visibility_toggle(self, widget):
        sender = self.sender()
       
        if type(widget) != QWidget:
            widget = self.find_text_widget(sender.objectName())

        if type(widget) == QWidget:
            if widget.isHidden():
                widget.setHidden(False)
            else:
                widget.setHidden(True)

    def on_create_button_clicked(self):
        new_file_content = ""
        for i in range(self.layout_right_textboxes.count()):
            item = self.layout_right_textboxes.itemAt(i)
            widget = item.widget()
            textEditBox = widget.findChild(QTextEdit)
            if widget.isHidden() == False:
                new_file_content += f"{textEditBox.toPlainText()}\n"

        api_put_data = {
            "type": "new_note",
            "filename": "/" + self.final_path_label.text(),
            "content": new_file_content,
        }
        self.dataSent.emit(api_put_data)
        self.close()

    def closeEvent(self, event):
        super().closeEvent(event)
