---
kind: rules
when: .NET XML doc comments (///)
default: auto
detect_files: *.sln, *.slnx, *.csproj, */*.csproj, Directory.Build.props
description: .NET XML doc comment conventions
---
## .NET XML docs
- Every public summary is one sentence, in the Microsoft phrasing for its member kind: "Gets or sets …", "Gets a value indicating whether …", "Initializes a new instance of the <see cref="T"/> class.". The rest of the sentence adds information.
- Write `<see langword="null"/>`, `<see langword="true"/>`, not the bare word. Use `<paramref name="x"/>` for a parameter in prose.
- Document each thrown exception with `<exception cref="T">`, saying the condition that throws it.
- Use `<inheritdoc/>` on overrides and interface implementations instead of copied text.
- With `GenerateDocumentationFile` and CS1591 on, docs are required: write real ones, never echo stubs.
