---
kind: rules
when: KDoc in .kt files
default: auto
detect_files: build.gradle.kts, settings.gradle.kts, */build.gradle.kts
description: KDoc and Dokka conventions for Kotlin
---
## KDoc
- The first paragraph is the summary. Write it in the third person.
- Link with `[name]` instead of `{@link}`. Document constructor properties with `@property`, not `@param`.
- Use Markdown. Never use Javadoc HTML tags in KDoc.
