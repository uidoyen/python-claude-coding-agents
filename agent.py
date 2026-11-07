"""A small coding agent: it reads a codebase with three tools and edits only after you say yes.

Run:  uv run agent.py "Why does checkout charge twice?"
"""
import difflib
import subprocess
import sys
from pathlib import Path

import anthropic

ROOT = Path(".").resolve()  # the agent can only see files under this folder
MAX_STEPS = 15              # stop even if the model keeps asking for tools
client = anthropic.Anthropic()

TOOLS = [
    {"name": "list_files", "description": "List every file in the project.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "search", "description": "Find lines that contain some text. Returns file:line: text.",
     "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "read_file", "description": "Read one file, with line numbers.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "edit_file", "description": "Replace one exact piece of text in a file. The user must approve it.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
         "required": ["path", "old", "new"]}},
]


def safe_path(path):
    full = (ROOT / path).resolve()
    if not full.is_relative_to(ROOT):
        raise ValueError(f"{path} is outside the project")
    return full


def list_files():
    files = [p for p in ROOT.rglob("*") if p.is_file() and not any(part.startswith((".", "__")) for part in p.parts)]
    return "\n".join(str(p.relative_to(ROOT)) for p in sorted(files))


def search(text):
    out = subprocess.run(["grep", "-rn", "--include=*.py", text, "."], cwd=ROOT, capture_output=True, text=True)
    return out.stdout or "No matches."


def read_file(path):
    lines = safe_path(path).read_text().splitlines()
    return "\n".join(f"{n}: {line}" for n, line in enumerate(lines, 1))


def edit_file(path, old, new):
    file = safe_path(path)
    before = file.read_text()
    if before.count(old) != 1:
        return "Error: the old text must appear exactly once."
    after = before.replace(old, new)
    diff = difflib.unified_diff(before.splitlines(), after.splitlines(), path, path, lineterm="")
    print("\n".join(diff))
    if input("Apply this fix? [y/N] ").strip().lower() != "y":
        return "The user said no. Do not change the file."
    file.write_text(after)
    return "Done. The file is changed."


def run_tool(name, args):
    try:
        return {"list_files": list_files, "search": search,
                "read_file": read_file, "edit_file": edit_file}[name](**args)
    except Exception as error:
        return f"Error: {error}"


def ask(question):
    messages = [{"role": "user", "content": question}]
    for step in range(MAX_STEPS):
        reply = client.beta.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=16000,
            system="You are a coding agent. Use the tools to look at the code before you answer. "
                   "Search first, then read only the files you need.",
            tools=TOOLS,
            messages=messages,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        messages.append({"role": "assistant", "content": reply.content})
        if reply.stop_reason != "tool_use":
            return "".join(block.text for block in reply.content if block.type == "text")

        results = []
        for block in reply.content:
            if block.type == "tool_use":
                print(f"-> {block.name}({block.input})")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": run_tool(block.name, block.input)})
        messages.append({"role": "user", "content": results})
    return "Stopped: too many steps."


if __name__ == "__main__":
    print(ask(" ".join(sys.argv[1:]) or "Why does checkout charge twice?"))
