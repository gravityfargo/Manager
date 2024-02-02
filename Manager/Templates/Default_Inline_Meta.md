%%
class:: 
parent:: 
created:: `$= dv.current().file.ctime.toFormat("f")`
modified:: `$= dv.current().file.mtime.toFormat("f")`
```dataviewjs
let folderPath = dv.current().file.folder;
let directories = folderPath.split('/');
let lastDirectory = directories[directories.length - 1];
let purposeString = `purpose:: ${lastDirectory}`;
dv.paragraph(purposeString);
```
%%
