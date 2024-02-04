clone the repo into your vault, run installer.py
systemwide python venv requred
be sure to enable both js queries in dataview
Install Plugins
  - Python Scripter
  - Dataview
  - Templater
  - Quickadd
  - Local REST API
  - Commander

## Directories
/Obsidian/
/Obsidian/Manager/Configs/
/Obsidian/Manager/Templates/

## Base Templates
- /Obsidian/Manager/Templates/`Button-Definitions`
- /Obsidian/Manager/Templates/`Header`
- /Obsidian/Manager/Templates/`Inline-Meta`
- /Obsidian/Manager/Templates/`Notes`
- /Obsidian/Manager/Templates/`PDF-Annotation`
- /Obsidian/Manager/Templates/`Root-Index`
- /Obsidian/Manager/Templates/`Sublevel-01-Index`
- /Obsidian/Manager/Templates/`Sublevel-02-Index`

## Configs
- /Obsidian/Manager/Configs/`config.md`

## Documentation
/Obsidian/Manager.md

## Things that will be made for you
A primary index:
- /Obsidian/Manager/Templates/Quicklinks-Courses-Testing
- /Obsidian/Manager/Templates/Quicklinks-Courses-Testing
- /Index.md
- /Courses-Testing/
- /Courses-Testing/Index.md
- /Courses-Testing/ECE214/
- /Courses-Testing/ECE214/Index.md
- /Courses-Testing/ECE214/Notes/
- /Courses-Testing/ECE214/Notes/Index.md
- /Courses-Testing/ECE214/Course Resources/
- /Courses-Testing/ECE214/Course Resources/Index.md
- /Courses-Testing/ECE214/Homework/
- /Courses-Testing/ECE214/Homework/Index.md
- /Courses-Testing/ECE214/Labs/
- /Courses-Testing/ECE214/Labs/Index.md
- /Courses-Testing/ECE214/References/
- /Courses-Testing/ECE214/References/Index.md

## modifications to other configs
templater
```
  "enable_folder_templates": true,
  "folder_templates": [
    {
      "folder": "Courses-Testing/ECE214/Notes",
      "template": "Obsidian/Manager/Templates/Notes"
    },
    {
      "folder": "Courses-Testing/ECE214/Course Resources",
      "template": "Obsidian/Manager/Templates/Notes"
    }
    . . .
  ],
```
