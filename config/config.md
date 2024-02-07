````json primary-config
{
	"rest-api-url": "http://127.0.0.1:27123",
	"default-note-name": "Raw Note.md"
}
primary-config```

```json directory-config
{
	"Courses": {
		"naming": {
			"Course": "tab"
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
