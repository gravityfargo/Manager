````json primary-config
{
	"rest-api-key": "06ea7e98a1ef3157e10908f3715ce178a8baf02bf39b62b0b83e2561a6ada94e",
	"rest-api-url": "http://127.0.0.1:27123",
	"index-template": "Index",
	"templates-list": [
		"Default_Contents", 
		"Default_Header", 
		"Quicklinks"
		],
	"templates-components-list": [
		"Index_Template", 
		"Notes_Template"
		],
	"default-note-name": "Raw Note.md"
}
primary-config```

```json directory-config
{
	"Courses": {
		"naming": {
			"Course": ["tabs"]
		},
		"directories": {
			"ECE214": [
				"Notes",
				"Course Resources",
				"Homework",
				"Labs",
				"References"
			],
			"ECE271": [
				"Notes",
				"Course Resources",
				"Homework",
				"Labs",
				"References"
			],
			"ECE331": [
				"Notes",
				"Course Resources",
				"Homework",
				"Projects",
				"References"
			]
		}
	},
	"Linux Reference": {
		"naming": {
			"category": ["programs"]
		},
		"directories": {
			"networking": ["netplan"],
			"System Manager": ["systemd", "initd"],
			"Resource Manager": ["cgroups"]
		}
	}
}
directory-config```

```markdown default-frontmatter
---
TBD
---
default-frontmatter```

```markdown default-inline-meta
%%
created:: `$= dv.current().file.ctime.toFormat("f")`
modified:: `$= dv.current().file.mtime.toFormat("f")`
```dataviewjs
let folderPath = dv.current().file.folder;
let directories = folderPath.split('/');
let lastDirectory = directories[directories.length - 1];
let purposeString = `purpose:: ${lastDirectory}`;
dv.paragraph(purposeString);
````

%%
default-inline-meta```