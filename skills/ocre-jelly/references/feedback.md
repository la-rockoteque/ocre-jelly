# Feedback

When the user asks for something ocre-jelly doesn't do (a language, a locale, a convention, a doc format, a tool integration, a check), say so plainly first. Name the closest thing that exists, if any. Then offer, with AskUserQuestion, to send a feature request to the author. For `/ocre-jelly feedback`, skip the offer.

1. Draft the text: one line for the request, one for why the user needs it, and any detail they gave. Use the ocre-jelly writing rules.
2. Leave out code, file contents, file paths, repo, product and customer names, people's names and anything secret, unless the user explicitly adds them.
3. Show the exact text, and ask the user to confirm or edit it. Ask whether to add a contact (an email or a name) and whether to include the context line (version, locales, Python version).
4. After they confirm, run:
   ```bash
   python3 <this-skill-dir>/scripts/feedback.py --kind feature|bug|feedback --message "<text>" [--why "<use case>"] [--contact "<contact>"] [--no-context] --open
   ```
   Pass the text as an argument or on stdin, never interpolated unquoted into the shell. The script opens the form in the browser, pre-filled. Tell the user that nothing is sent until they click **Submit** there.
5. Never submit the form yourself, and never send feedback without the user's confirmation. If `feedback.enabled` is false in the config, say that feedback is turned off in this repo.
