/**
 * QuickAdd Script: Create Area with Base file
 * Base files are now stored in System/Bases/
 */

const app = this.app;
const QuickAdd = this.QuickAdd;

QuickAdd.prompt("Jméno oblasti:").then(areaName => {
  if (!areaName) {
    console.log("Zrušeno uživatelem");
    return;
  }

  // Slug
  const slug = areaName
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w\-]/g, "");

  const areaFolderPath = `Oblasti/${areaName}`;
  const rootNotePath = `${areaFolderPath}/${slug}.md`;
  const baseFilePath = `System/Bases/${slug}-oblast.base`;

  const rootNoteTemplate = `---
start_date: ${new Date().toISOString().split('T')[0]}
due_date:
tags: []
status: To Do
---

# ${areaName}

## Quick Info
Popis oblasti...

---

## Projekty

![[/System/Bases/${slug}-oblast.base#Projekty]]

---

## Tasks

![[/System/Bases/${slug}-oblast.base#Tasks]]

---

## Notes

![[/System/Bases/${slug}-oblast.base#Notes]]
`;

  const baseFileContent = `filters:
  and:
    - file.inFolder("Oblasti")
properties:
  start_date:
    displayName: "Start"
  due_date:
    displayName: "Due"
  status:
    displayName: "Status"
views:
  - type: table
    name: "Projekty"
    filters:
      and:
        - file.hasTag("project")
        - note.area.some(file.name == "${slug}")
    columns:
      - file.name
      - status
      - due_date
    order:
      - status
      - due_date
      - file.name
    sort:
      - property: status
        direction: ASC
  - type: table
    name: "Tasks"
    filters:
      and:
        - file.hasTag("task")
        - list(areas).some(file.name == "${slug}")
    columns:
      - file.name
      - status
      - due
      - projects
    order:
      - status
      - due
      - file.name
    sort:
      - property: status
        direction: ASC
  - type: table
    name: "Notes"
    filters:
      and:
        - file.inFolder("${areaFolderPath}")
        - file.ext == "md"
        - file.name != "${slug}"
    columns:
      - file.name
      - file.mtime
    order:
      - file.mtime
      - file.name
    sort:
      - property: file.mtime
        direction: DESC
`;

  // Vytvoř složku oblasti
  app.vault.adapter.mkdir(areaFolderPath).then(() => {
    // Paralelně vytvoř root note a base soubor
    Promise.all([
      app.vault.create(rootNotePath, rootNoteTemplate),
      app.vault.create(baseFilePath, baseFileContent)
    ]).then(([rootNoteFile]) => {
      // Otevři root note
      if (rootNoteFile) {
        app.workspace.getLeaf().openFile(rootNoteFile);
      }
      console.log(`✅ Oblast vytvořena: ${areaName}`);
      console.log(`📁 Složka: ${areaFolderPath}`);
      console.log(`📄 Root note: ${rootNotePath}`);
      console.log(`📊 Base soubor: ${baseFilePath}`);
    }).catch(err => {
      console.error("Chyba při vytváření souborů:", err);
    });
  }).catch(err => {
    console.error("Chyba při vytváření složky:", err);
  });
});
