# Global Storyboard Pipeline

This folder contains the reusable storyboard pipeline.

Main workflow:

`scene-pack.md` -> `short-drama-shot-planner` -> `short-drama-shot-review` -> `short-drama-shot-prompt` -> `short-drama-shot-review` -> `storyboard.json` / `storyboard.md` -> `short-drama-reference-linker` -> `linked-storyboard.json` -> `short-drama-start-image-review`

Reusable downstream image generation is also available here:

- `generate_comfy_image_set.py`

All runtime outputs should go into the target project's `output` folder.

Schema notes:

- planner output is lean shot task only
- planned shots are structurally reviewed before prompt generation
- prompt generation is LLM-only in the formal pipeline
- generated prompts are reviewed again for Qwen cleanliness before assembly
- prompt output is one canonical `image_prompt`
- post-storyboard reference linking produces a separate `resolved_image_prompt`
- panel text uses `panelTextType` + `panelText`
- `start_image_prompt` is retired
- `dialogueText` / `captionText` are retired
- `reference_preservation_clause` / `prompt_risk_note` are not main shot fields anymore

## Main Command

```powershell
python "C:\Users\anson\Desktop\writing\out\script\run_storyboard_pipeline.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>" `
  --executor command `
  --command-template "python C:\Users\anson\Desktop\writing\out\script\codex_shot_prompt_adapter.py --request {request} --response {response}"
```

If the command bridge is missing, the formal pipeline should fail fast instead of silently falling back to heuristic prompt writing.

## No-API / No-Bridge MCP-in-Chat Workflow

If you do not have an API key and cannot use `CODEX_MCP_COMMAND`, use file handoff:

1. Plan shots
```powershell
python "C:\Users\anson\Desktop\writing\out\script\plan_storyboard_shots.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

2. Review planned shots
```powershell
python "C:\Users\anson\Desktop\writing\out\script\review_planned_shots.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>" `
  --executor command `
  --command-template "python C:\Users\anson\Desktop\writing\out\script\codex_shot_prompt_adapter.py --request {request} --response {response}"
```

3. Export prompt requests for this chat to consume
```powershell
python "C:\Users\anson\Desktop\writing\out\script\export_shot_prompt_requests.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

4. Ask Codex in chat to read `output\storyboard-workspace\log\requests\*_prompt_request.json` and write matching `*_prompt_response.json`

5. Apply prompt responses
```powershell
python "C:\Users\anson\Desktop\writing\out\script\apply_shot_prompt_responses.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

6. Export prompt-review requests
```powershell
python "C:\Users\anson\Desktop\writing\out\script\export_shot_prompt_review_requests.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

7. Ask Codex in chat to write matching `*_prompt_review_response.json`

8. Apply prompt-review responses
```powershell
python "C:\Users\anson\Desktop\writing\out\script\apply_shot_prompt_review_responses.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

9. Assemble storyboard
```powershell
python "C:\Users\anson\Desktop\writing\out\script\assemble_storyboard.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

10. Export/apply reference-linking requests
```powershell
python "C:\Users\anson\Desktop\writing\out\script\link_storyboard_references.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>"
```

Then ask Codex in chat to read `output\reference-linking\requests\*_reference_link_request.json` and write matching `*_reference_link_response.json`.

Re-run the same command to apply the responses and refresh `linked-storyboard.json`.

## Outputs

By default, a project writes to:

- `<project-dir>\output\storyboard-workspace`
- `<project-dir>\output\storyboard-workspace\log\requests`
- `<project-dir>\output\storyboard-workspace\log\responses`
- `<project-dir>\output\storyboard-workspace\log\reviews`
- `<project-dir>\output\storyboard.json`
- `<project-dir>\output\storyboard.md`
- `<project-dir>\output\reference-linking\requests`
- `<project-dir>\output\reference-linking\responses`
- `<project-dir>\output\linked-storyboard.json`
- `<project-dir>\output\generated`
- `<project-dir>\output\logs`

Do not treat `short-drama-storyboard` as the main pipeline skill.
It is legacy reference only.

## Global Comfy Image Command

```powershell
python "C:\Users\anson\Desktop\writing\out\script\generate_comfy_image_set.py" `
  --project-dir "C:\Users\anson\Desktop\writing\out\<your-project>" `
  --phase full
```
