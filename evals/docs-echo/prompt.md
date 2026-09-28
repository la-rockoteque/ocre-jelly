---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Review the doc comments in this TypeScript file for AI-generated or useless documentation. Report findings only.

```ts
/**
 * Gets the user name.
 * @param userId The user id.
 * @returns The result.
 */
export function getUserName(userId: number): string { return lookup(userId).name; }

/**
 * Retries the request three times with exponential backoff, then throws the last error.
 * @param attempt Zero-based attempt counter; values above 2 throw immediately.
 */
export function retry(attempt: number): void { /* ... */ }
```
