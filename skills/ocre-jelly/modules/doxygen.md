---
kind: rules
when: C/C++ Doxygen comments
default: auto
detect_files: Doxyfile, doxygen.conf
description: Doxygen conventions for C and C++
---
## Doxygen
- Use one comment style per project (`///` or `/** */`) and one command prefix (`@` or `\`). Follow the one the file already uses.
- The first sentence is the brief. Don't repeat `@brief` when autobrief is on.
- Write `@param[in]`/`@param[out]` for pointer parameters, and `@retval` for each distinct return code.
