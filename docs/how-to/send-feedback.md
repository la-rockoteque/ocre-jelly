# Send feedback

Ask for a feature, report a bug, or leave a comment for the ocre-jelly author. The feedback goes to [this form](https://forms.gle/GwKgxKB23iSKyZqr7).

## From Claude Code

```
/ocre-jelly feedback Support Spanish (es-MX); half our docs are in Spanish.
```

Claude also offers it on its own: when you ask for something ocre-jelly doesn't support, it says so, names the closest thing that exists, and asks whether to send a feature request.

What happens next:

1. Claude drafts the text: the request, why you need it, and your details.
2. It shows you the exact text. You confirm it or edit it. It asks whether to add a contact and whether to include the context line.
3. It opens the form in your browser, with the text filled in.
4. You read it there and click **Submit**. Nothing is sent before that.

The draft never includes code, file contents, file paths, repo, product or customer names, or people's names, unless you add them yourself. The context line holds only the ocre-jelly version, the configured locales and the Python version.

## Without Claude

Open [the form](https://forms.gle/GwKgxKB23iSKyZqr7) and write your feedback. Or build a pre-filled link with the script:

```bash
python3 $OJ/feedback.py --kind bug --message "The glossary parser misses my 5-column tables" --open
```

See [Command line](../reference/cli.md#feedbackpy-feedback-to-the-author) for every option.

## Use your own form, or turn it off

A company that wants feedback to go to its own team can point the command at another Google Form:

1. Create a form with one **Paragraph** question.
2. In the form's menu, choose **Get pre-filled link**. Type `x` in the question, then copy the link. It contains `entry.<digits>=x`.
3. Set both values in the repo:

   ```bash
   python3 $OJ/modules.py config set feedback '{"form_url":"https://docs.google.com/forms/d/e/<id>/viewform","entry":"<digits>"}' --project
   ```

To turn feedback off in a repo, so Claude neither offers it nor sends it:

```bash
python3 $OJ/modules.py config set feedback '{"enabled":false}' --project
```

The form URL must use `https`. `feedback.py` shows the form's host before it opens anything.
