import os
import subprocess
import sys

import requests


def get_pr_review_comments(repo: str, pr_number: str, token: str) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def build_aider_prompt(comments: list[dict]) -> str:
    lines = ["Fix the following PR review comments:\n"]
    for c in comments:
        path = c.get("path", "")
        line = c.get("line") or c.get("original_line", "")
        body = c.get("body", "")
        lines.append(f"- File `{path}` line {line}: {body}")
    return "\n".join(lines)


def run_aider(prompt: str, model: str, files: list[str]) -> None:
    cmd = [
        "aider",
        "--yes",
        "--no-git",
        "--model", model,
        "--message", prompt,
        *files,
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def push_changes(branch: str, repo: str, token: str) -> None:
    remote = f"https://x-access-token:{token}@github.com/{repo}.git"
    subprocess.run(["git", "config", "user.email", "action@github.com"], check=True)
    subprocess.run(["git", "config", "user.name", "GitHub Action"], check=True)
    subprocess.run(["git", "add", "-A"], check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print("No changes to commit.")
        return
    subprocess.run(["git", "commit", "-m", "fix: address PR review comments via aider"], check=True)
    subprocess.run(["git", "push", remote, f"HEAD:{branch}"], check=True)


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    branch = os.environ["PR_BRANCH"]
    model = os.environ.get("AIDER_MODEL", "gpt-4o")

    comments = get_pr_review_comments(repo, pr_number, token)
    if not comments:
        print("No review comments found.")
        return

    prompt = build_aider_prompt(comments)
    files = list({c["path"] for c in comments if c.get("path")})
    print(f"Running aider with prompt:\n{prompt}\nFiles: {files}\n")
    run_aider(prompt, model, files)
    push_changes(branch, repo, token)


if __name__ == "__main__":
    main()
