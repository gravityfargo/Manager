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
				"Unprocessed Notes",
				"Course Resources",
				"Homework",
				"Labs",
				"References"
			],
			"ECE271": [
				"Notes",
				"Unprocessed Notes",
				"Course Resources",
				"Homework",
				"Labs",
				"References"
			],
			"ECE331": [
				"Notes",
				"Unprocessed Notes",
				"Course Resources",
				"Homework",
				"Projects",
				"References"
			]
		}
	},
	"Linux Reference": {
		"naming": {
			"category": "tab"
		},
		"directories": {
			"networking": ["netplan"],
			"System Manager": ["systemd", "initd"],
			"Resource Manager": ["cgroups"]
		}
	},
	"ARCSIM": {
		"naming": {
			"Category": "programs"
		},
		"directories": {
			"Slurm": [""],
			"Munge": [""],
			"Infiniband": [""]
		}
	}
}
directory-config```

