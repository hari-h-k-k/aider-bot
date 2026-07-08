import os
import subprocess
import sys

import requests


def run_aider(prompt: str, model: str) -> None:
    cmd = ["aider", "--yes", "--no-git", "--model", model, "--message", prompt]
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
    branch = os.environ["PR_BRANCH"]
    model = os.environ.get("AIDER_MODEL", "morph/morph-minimax3-428b")
    comment_body = os.environ["COMMENT_BODY"]

    prompt = comment_body.removeprefix("/aiderfix").strip()
    if not prompt:
        print("No instruction provided after /aiderfix.")
        return

    print(f"Running aider with prompt:\n{prompt}\n")
    run_aider(prompt, model)
    push_changes(branch, repo, token)


if __name__ == "__main__":
    main()
