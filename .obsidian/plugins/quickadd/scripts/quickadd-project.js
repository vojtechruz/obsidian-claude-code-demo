/**
 * QuickAdd Script: Create Project with Base file
 * Base files are now stored in System/Bases/
 */

const app = this.app;
const QuickAdd = this.QuickAdd;

QuickAdd.prompt("Jméno projektu:").then(projectName => {
  if (!projectName) {
    console.log("Zrušeno uživatelem");
    return;
  }

  // Slug
  const slug = projectName
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w\-]/g, "");

  const projectFolderPath = `Projekty/${projectName}`;
  const rootNotePath = `${projectFolderPath}/${slug}.md`;
  const baseFilePath = `System/Bases/${slug}-projekt.base`;

  const rootNoteTemplate = `---
area:
start_date: ${new Date().toISOString().split('T')[0]}
due_date:
tags: [project]
status: To Do
---

# ${projectName}

## Quick Info
Krátký popis projektu...

## Poznámky
-

---

## Tasks

![[/System/Bases/${slug}-projekt.base#Tasks]]

---

## Notes

![[/System/Bases/${slug}-projekt.base#Notes]]
`;

  const baseFileContent = `filters:
  and:
    - file.hasTag("project")
    - file.name == "${slug}"
properties:
  area:
    displayName: "Area"
  start_date:
    displayName: "Start"
  due_date:
    displayName: "Due"
  status:
    displayName: "Status"
views:
  - type: table
    name: "Tasks"
    filters:
      and:
        - file.hasTag("task")
        - list(projects).some(file.name == "${slug}")
    columns:
      - file.name
      - status
      - due
      - priority
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
        - file.inFolder("${projectFolderPath}")
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

  // Vytvoř složku projektu
  app.vault.adapter.mkdir(projectFolderPath).then(() => {
    // Paralelně vytvoř root note a base soubor
    Promise.all([
      app.vault.create(rootNotePath, rootNoteTemplate),
      app.vault.create(baseFilePath, baseFileContent)
    ]).then(([rootNoteFile]) => {
      // Otevři root note
      if (rootNoteFile) {
        app.workspace.getLeaf().openFile(rootNoteFile);
      }
      console.log(`✅ Projekt vytořen: ${projectName}`);
      console.log(`📁 Složka: ${projectFolderPath}`);
      console.log(`📄 Root note: ${rootNotePath}`);
      console.log(`📊 Base soubor: ${baseFilePath}`);
    }).catch(err => {
      console.error("Chyba při vytváření souborů:", err);
    });
  }).catch(err => {
    console.error("Chyba při vytváření složky:", err);
  });
});
