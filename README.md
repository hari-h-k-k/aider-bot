# aider-pr-review-fixer

A GitHub Action that automatically fixes PR review comments using [aider](https://github.com/paul-gauthier/aider).

When triggered on a pull request review, it reads all inline review comments, passes them to aider as a prompt, and pushes the resulting fixes back to the PR branch.

## Usage

Create a workflow file in your repo at `.github/workflows/fix-review.yml`:

```yaml
name: Fix PR Review Comments

on:
  pull_request_review:
    types: [submitted]

jobs:
  fix:
    runs-on: ubuntu-latest
    if: github.event.review.state == 'changes_requested'
    permissions:
      contents: write
      pull-requests: read
    steps:
      - uses: your-org/aider-pr-review-fixer@main
        with:
          morph_api_key: ${{ secrets.MORPH_API_KEY }}
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `morph_api_key` | Yes | — | Morph API key used by aider |
| `github_token` | No | `github.token` | GitHub token with `contents: write` and `pull-requests: read` |
| `model` | No | `morph/morph-minimax3-428b` | LLM model for aider |

## Using a different model

Override the `model` input with any aider-supported model name:

```yaml
- uses: your-org/aider-pr-review-fixer@main
  with:
    morph_api_key: ${{ secrets.MORPH_API_KEY }}
    model: morph/morph-minimax3-428b
```

## How it works

1. Fetches all inline review comments from the PR via GitHub API.
2. Builds a single prompt describing each comment (file, line, message).
3. Runs `aider --yes --no-git --message "<prompt>"` in the checked-out PR branch.
4. Commits and pushes any changes aider makes back to the PR branch.

## Permissions required

```yaml
permissions:
  contents: write      # to push fixes
  pull-requests: read  # to read review comments
```

## Secrets required

Add `MORPH_API_KEY` to your repository secrets under **Settings → Secrets and variables → Actions**.
