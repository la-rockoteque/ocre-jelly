---
kind: rules
when: Javadoc in .java files
default: auto
detect_files: pom.xml, build.gradle, build.gradle.kts, settings.gradle, settings.gradle.kts, */pom.xml, */build.gradle, */build.gradle.kts
description: Javadoc conventions for Java
---
## Javadoc
- The first sentence is the summary. It ends at the first period followed by a space, so never put "e.g. " or "i.e. " in it.
- Use the third person: "Returns the …", not "Return the …" or "This method returns …".
- Write `@param name description` with no hyphen and `@return`, never `@returns`. Wrap code in `{@code …}`.
- Don't add `@author` or `@version`, because git records both.
