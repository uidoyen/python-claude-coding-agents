# A tiny coding agent in Python

The code from "How Coding Agents Actually Work (Build One From Scratch in Python)".

`agent.py` (about 100 lines) gives a Claude model four tools: `list_files`, `search`, `read_file` and `edit_file`. It runs them in
a loop until the model can answer. `edit_file` shows the diff and changes nothing until you type `y`.

`shop/` is a small example app with a bug: one checkout charges the card twice.

```bash
uv run python -m shop.demo                            # see the bug: two charges
export ANTHROPIC_API_KEY=...                         # your key
cd shop && uv run ../agent.py "Why does checkout charge twice?"
```

The agent can only see files under the folder you run it from (here `shop/`, six files), and it stops after 15 steps.
