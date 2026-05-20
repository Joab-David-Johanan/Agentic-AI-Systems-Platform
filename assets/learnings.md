# Learnings from this project

#### Q. How to untrack the .git folder, as I see it in my VSCode file explorer?

- The .git folder is the git repository itself — it contains all your commit history, branches, and config. Git never tracks it and you cannot untrack it.

- What you're likely seeing in VSCode is the folder just being visible in the file explorer. To hide it, add this to your VSCode settings.json:

```bash
"files.exclude": {
  "**/.git": true
}
```

#### Q. How to untrack committed files and directories in .gitignore?

- .gitignore only prevents future tracking — it doesn't untrack things already in the index.
If you're trying to untrack a file/folder that was already committed,  You need to remove it from the index:

Untrack a single file (keeps it on disk)

```bash
git rm --cached <file>
```

Untrack a whole directory

```bash
git rm --cached -r <directory>
```

#### Q. Why do we create the `src/` folder in our project structure?

- `src/` is just a folder layout convention to keep the source code separate from config files, notebooks, data, etc.

#### Q. Why do we use `__init__.py`?

- We use `__init__.py` for folders we intend to import as packages.

#### Q. What happens with ***editable install***?

- ***editable install*** makes your own package (in our current project `research_system`) importable from anywhere in your project using clean imports, without needing to worry about where Python was launched from.

- It does this by dropping a `.pth` file into `site-packages` that permanently tells Python always add `src/` to `sys.path` so `research-system` is always findable regardless of where you launch Python from.

- Without ***editable install*** your imports are fragile, they break depending on where Python was launched from.
    - Python can import only packages it can see - meaning the folder must be on its search path (sys.path)
    - By default, Python adds your current working directory to the path.


- When you have a `pyproject.toml` file and run the command `pip install -e .` you are using ***editable install*** where Python adds `src/` to `sys.path` and it is completed bypassed as import path.
- `research_system` becomes the top-level package and src is completely invisible to Python.
- So you imports become `research_system.agent.search_agent import SearchAgent` not `src.research_system.agent.search_agent import SearchAgent`

---

## Moving from Conda to uv

#### Q. Why did we switch this project from Conda to uv?

- Conda is useful for heavy data science environments, especially when you need system-level native packages.
- For this project, `uv` is cleaner because this is a Python package/application with dependencies declared in `pyproject.toml`.
- `uv` gives us:
  - a local project virtual environment in `.venv/`
  - dependency management through `pyproject.toml`
  - reproducible installs through `uv.lock`
  - editable install of our own package
  - fast installs and clean commands

The important idea:

```text
pyproject.toml = what the project needs
uv.lock = exact resolved package versions
.venv/ = local installed environment, not committed to git
```

#### Q. What commands did we use during the migration?

Check the old Conda environments:

```bash
conda env list
```

Why:

- This lists Conda environments so we can confirm that `agent-env` exists.
- In our case, Conda hit a plugin permission issue on Windows, so we used Conda with plugins disabled for the removal step.

Remove the old Conda environment:

```bash
CONDA_NO_PLUGINS=true conda env remove -n agent-env -y
```

PowerShell version:

```powershell
$env:CONDA_NO_PLUGINS='true'
conda env remove -n agent-env -y
```

Why:

- `conda env remove -n agent-env -y` deletes the Conda environment named `agent-env`.
- `CONDA_NO_PLUGINS=true` disables Conda plugins for that command, which avoided the Windows permission error we saw.
- This does not delete the project. It only deletes the old Conda environment.

Check uv is installed:

```bash
uv --version
```

Why:

- This confirms that the `uv` command is available on the machine.

Create a local uv virtual environment with Python 3.12:

```bash
uv venv --python 3.12
```

Why:

- This creates `.venv/` in the project root.
- It uses Python 3.12.
- If Python 3.12 is not already installed, uv can use/download a managed Python runtime.
- `.venv/` is local to the project and should stay ignored by git.

Install dependencies and install this project:

```bash
uv sync
```

On Windows, if certificate validation fails, use:

```bash
uv sync --native-tls
```

Why:

- `uv sync` reads `pyproject.toml` and `uv.lock`.
- If `uv.lock` does not exist, uv resolves dependencies and creates it.
- It installs all project dependencies into `.venv/`.
- It also installs the current project itself.
- Because this project uses a `src/` layout and package metadata in `pyproject.toml`, uv installs the package in editable mode for development.

In our environment, `uv sync --native-tls` was needed because PyPI certificate validation failed with uv's bundled certificate handling. `--native-tls` tells uv to use the Windows native certificate store.

Verify the Python version:

```bash
.venv\Scripts\python.exe --version
```

Why:

- This confirms the actual Python interpreter inside `.venv/`.
- In our case it showed Python 3.12.11.

Verify the package import:

```bash
.venv\Scripts\python.exe -c "import research_system, sys; print(sys.executable); print(research_system.__file__)"
```

Why:

- This confirms Python is using the `.venv/` interpreter.
- It also confirms that `research_system` imports from `src/research_system`.
- That proves the project package is importable with clean imports.

Verify editable install:

```bash
Get-ChildItem .venv\Lib\site-packages | Where-Object { $_.Name -like '*research*' }
```

Why:

- This shows the installed metadata for the local package.
- We saw `__editable__.research_system-0.1.0.pth`, which means the local project was installed editably.

#### Q. What should I do on a new machine from scratch?

Step 1: Clone the repo.

```bash
git clone <your-github-repo-url>
cd Multi-Agent-Research-System
```

Why:

- This downloads the project files.
- The repository should include `pyproject.toml` and `uv.lock`.
- It should not include `.venv/`, because virtual environments are machine-specific.

Step 2: Open the folder in VSCode.

```bash
code .
```

Why:

- Open the project root, not the `src/` folder.
- VSCode should see `pyproject.toml`, `uv.lock`, `src/`, `tests/`, and other project files from the root.

Step 3: Create the uv virtual environment with Python 3.12.

```bash
uv venv --python 3.12
```

Why:

- This creates a fresh `.venv/` for this project.
- The environment is isolated from global Python, Conda, and other projects.

Step 4: Install everything from the project metadata.

```bash
uv sync
```

If TLS/certificate errors happen on Windows:

```bash
uv sync --native-tls
```

Why:

- `uv sync` reads the project dependency metadata.
- It installs the dependencies listed in `pyproject.toml`.
- If `uv.lock` exists, it uses the exact locked versions from `uv.lock`.
- It installs this project itself into `.venv/`.
- It makes clean imports work:

```python
from research_system.pipelines.research_pipeline import run_research_pipeline
```

This matters because the actual package lives under:

```text
src/research_system/
```

Without installing the package, Python may only know about the current working directory. That can make imports fragile, especially from notebooks or scripts in subfolders.

After `uv sync`, the package is available through the environment, so imports work from places like:

```text
main.py
notebooks/testing.ipynb
tests/test_pipeline.py
```

Important note for notebooks:

- The notebook must use the `.venv/` Python interpreter/kernel.
- If VSCode/Jupyter is using a different Python environment, clean imports may still fail.

Step 5: Run project commands through uv.

```bash
uv run python main.py
```

or, if needed on Windows:

```bash
uv run --native-tls python main.py
```

Why:

- `uv run` runs the command inside the project environment.
- You do not have to manually activate `.venv/`.

You can also activate the environment manually:

```powershell
.venv\Scripts\activate
```

Then run:

```bash
python main.py
```

Both approaches are valid. `uv run` is usually cleaner because it always uses the right project environment.

#### Q. When should I use `uv add`?

Use `uv add` when you want to add a new runtime dependency to the project.

Example:

```bash
uv add torch
```

Why:

- This adds `torch` to `pyproject.toml`.
- It updates `uv.lock`.
- It installs `torch` into `.venv/`.

So normally you do not need to immediately run `uv sync` after `uv add`.

This is the key distinction:

```text
uv add <package> = add a new dependency and install it now
uv sync = install/sync the environment from pyproject.toml and uv.lock
```

Use `uv add` for new packages:

```bash
uv add langgraph
uv add chromadb
uv add fastapi uvicorn
```

Use `uv add --dev` for development-only tools:

```bash
uv add --dev pytest ruff mypy black
```

Why:

- Runtime dependencies are needed by the application itself.
- Dev dependencies are only needed for development, testing, linting, or formatting.

#### Q. When should I use `uv sync`?

Use `uv sync` when you want the local `.venv/` to match the project files.

Common cases:

- after cloning the repo on a new machine
- after pulling changes from GitHub
- after someone else updates `pyproject.toml` or `uv.lock`
- after deleting `.venv/`
- when the environment feels out of sync

Command:

```bash
uv sync
```

Windows TLS fallback:

```bash
uv sync --native-tls
```

Why:

- It makes `.venv/` match the dependency definitions.
- It installs missing packages.
- It removes packages that are no longer part of the project, depending on uv's sync behavior.
- It installs the project package so clean imports work.

#### Q. When should I use `uv run`?

Use `uv run` when you want to run a command inside the project environment.

Examples:

```bash
uv run python main.py
uv run pytest
uv run streamlit run ui/app.py
uv run python -m compileall src main.py ui
```

Why:

- It avoids accidentally using the wrong Python interpreter.
- It uses the `.venv/` environment managed by uv.
- It works even if you did not activate `.venv/`.

#### Q. Do I still need `pip install -e .`?

No, not when using uv for this project.

Previously, with pip, editable install was:

```bash
pip install -e .
```

With uv, use:

```bash
uv sync
```

Why:

- `uv sync` installs dependencies and the current project.
- For local development, uv creates an editable-style install so code changes in `src/` are immediately reflected without reinstalling.

#### Q. Should I use `pip` inside the uv environment?

Prefer not to.

Use:

```bash
uv add <package>
uv add --dev <package>
uv sync
uv run <command>
```

Why:

- If you install packages manually with pip, `pyproject.toml` and `uv.lock` may not know about them.
- That creates the same problem we had with Conda: the environment works locally, but the dependency list is incomplete.
- The goal is that a new machine can reproduce the environment from the repo files alone.

#### Q. Which files should be committed?

Commit:

```text
pyproject.toml
uv.lock
```

Do not commit:

```text
.venv/
```

Why:

- `pyproject.toml` says what dependencies the project needs.
- `uv.lock` records exact versions for reproducible installs.
- `.venv/` is local machine output and can be recreated with `uv sync`.

---

## Conventional Commit Messages

#### Q. What commit message should I use for `uv.lock`?

If only adding the lockfile:

```bash
chore: add uv lockfile for reproducible installs
```

If the commit also changes the project from Conda or manual dependency management to uv:

```bash
chore: migrate dependency management to uv
```

#### Q. What are common conventional commit types?

Use `feat` when adding a new user-visible capability:

```bash
feat: add LangGraph orchestration pipeline
```

Use `fix` when correcting a bug:

```bash
fix: handle missing Tavily API key gracefully
```

Use `docs` for README files, learning notes, architecture notes, or documentation-only changes:

```bash
docs: update README quick start instructions
```

Use `chore` for tooling, dependency management, config, or repo maintenance:

```bash
chore: add uv lockfile for reproducible installs
```

Use `test` when adding or updating tests:

```bash
test: add unit tests for web search tool
```

Use `refactor` when changing code structure without changing behavior:

```bash
refactor: split research pipeline into reusable workflow steps
```

Use `style` for formatting-only changes:

```bash
style: format code with ruff
```

Use `build` for packaging or build-system changes:

```bash
build: update project packaging configuration
```

Use `ci` for CI/CD configuration:

```bash
ci: add GitHub Actions test workflow
```

Use `perf` for performance improvements:

```bash
perf: cache scraped content to reduce repeated requests
```

#### Q. What commit messages fit the current project cleanup?

For the README rewrite:

```bash
docs: rewrite README around agentic platform architecture
```

For the uv learning notes:

```bash
docs: add uv environment and dependency workflow notes
```

For the uv lockfile:

```bash
chore: add uv lockfile for reproducible installs
```

---

## Branching Strategy

#### Q. What branch strategy should this project use?

Use this as the normal workflow:

```text
feature branches -> dev -> main
```

Meaning:

```text
main = production/stable branch
dev = integration branch for testing features together
feat/* = individual feature branches
```

Example branches:

```text
main
dev
feat/utils
feat/tools
feat/agents-and-chains
feat/pipeline
```

Why:

- `main` should stay stable and production-ready.
- feature branches keep individual work isolated.
- `dev` lets multiple features be tested together before they go to `main`.
- this is easier to understand than cherry-picking many commits later.
- it looks more like a real team workflow than committing everything directly to `main`.

#### Q. What is the normal workflow from new feature to production?

Step 1: Start from the latest `main`.

```bash
git checkout main
git pull origin main
```

Why:

- This makes sure the new work starts from the latest stable code.

Step 2: Create a feature branch.

```bash
git checkout -b feat/tools
```

Why:

- A feature branch isolates one focused piece of work.
- Examples: `feat/utils`, `feat/tools`, `feat/agents-and-chains`, `feat/pipeline`.

Step 3: Make changes and commit them.

```bash
git status
git add <files>
git commit -m "feat: add web search and scraping tools"
```

Why:

- `git status` shows what changed.
- `git add` stages the exact files you want in the commit.
- `git commit` creates a meaningful checkpoint.

Step 4: Push the feature branch.

```bash
git push -u origin feat/tools
```

Why:

- This publishes the branch to GitHub.
- `-u` links the local branch to the remote branch, so future pushes can use just `git push`.

Step 5: Open a PR from the feature branch into `dev`.

```text
base: dev
compare: feat/tools
```

Why:

- `dev` is where features are integrated.
- This keeps `main` clean until the full system has been tested.

Step 6: Merge the feature PR into `dev`.

Why:

- Now the feature is part of the integrated development version.
- Other features can be tested together with it.

Step 7: Test the full app on `dev`.

```bash
git checkout dev
git pull origin dev
uv sync
uv run python -m compileall src main.py ui
uv run python main.py
```

Why:

- `dev` contains the combined feature work.
- This is where integration bugs are most likely to appear.
- `uv sync` makes sure the environment matches the project metadata.
- `compileall` catches syntax/import issues early.

Step 8: Open a PR from `dev` into `main`.

```text
base: main
compare: dev
```

Why:

- This promotes the tested integrated version to production/stable.
- The PR should explain what was added, what was tested, and any known limitations.

Step 9: Merge the PR into `main`.

Why:

- `main` now contains the production-ready version.
- GitHub contributions usually count commits once they land on the default branch, commonly `main`.

#### Q. What does `git push -u origin feat/tools` actually do?

Command:

```bash
git push -u origin feat/tools
```

Meaning:

```text
local branch:  feat/tools
remote repo:   origin
remote branch: origin/feat/tools
```

This command takes the local branch named:

```text
feat/tools
```

and pushes it to the remote repository named:

```text
origin
```

On GitHub, this creates or updates a branch also called:

```text
feat/tools
```

In your local Git metadata, Git refers to the GitHub copy as:

```text
origin/feat/tools
```

So the relationship becomes:

```text
local feat/tools -> remote origin/feat/tools
```

#### Q. What is `origin`?

`origin` is Git's default nickname for the remote GitHub repository.

Check it with:

```bash
git remote -v
```

Example output:

```text
origin  https://github.com/your-username/Multi-Agent-Research-System.git (fetch)
origin  https://github.com/your-username/Multi-Agent-Research-System.git (push)
```

Why:

- Writing the full GitHub URL every time would be annoying.
- Git uses `origin` as a short name for that remote repository.

#### Q. What does `-u` mean?

`-u` means:

```text
set upstream
```

It tells Git:

```text
My local feat/tools branch should track origin/feat/tools.
```

After this, Git remembers:

```text
feat/tools tracks origin/feat/tools
```

Why:

- Future pushes can use just `git push`.
- Future pulls can use just `git pull`.
- Git knows which remote branch the current local branch should sync with.

Before upstream is set, you usually need:

```bash
git push origin feat/tools
```

After upstream is set, while you are on `feat/tools`, you can use:

```bash
git push
git pull
```

Git understands:

```text
push local feat/tools to origin/feat/tools
pull origin/feat/tools into local feat/tools
```

#### Q. What is local vs remote?

Local branch:

```text
feat/tools
```

This branch lives on your machine. It is the branch you edit, commit to, and test locally.

Remote repository:

```text
origin
```

This is the GitHub repository your local repo is connected to.

Remote branch:

```text
origin/feat/tools
```

This is Git's local reference to the branch on GitHub. It represents what GitHub had the last time you fetched or pushed.

The mental model:

```text
feat/tools        = your editable local branch
origin            = nickname for the GitHub repo
origin/feat/tools = your local reference to the GitHub branch
```

#### Q. How do I check which remote branch my local branch tracks?

Command:

```bash
git branch -vv
```

Example output:

```text
* feat/tools  abc1234 [origin/feat/tools] feat: add tool integrations
  main        def5678 [origin/main] docs: update README
```

Meaning:

- `feat/tools` is the current local branch.
- `[origin/feat/tools]` is the upstream branch it tracks.
- `main` tracks `origin/main`.

Why:

- This helps confirm that pushes and pulls are going to the branch you expect.
- It is useful when working with many feature branches.

#### Q. Should I use a release branch?

For this project right now, usually no.

The simpler workflow is:

```text
feat/* -> dev -> main
```

A release branch is useful later when the project has a real release process:

```text
dev -> release/v0.1.0 -> main
```

Use a release branch when:

- you are preparing a versioned release
- you need a QA/staging freeze
- `dev` needs to keep moving while the release is stabilized
- you need last-minute release fixes before production

Commands:

```bash
git checkout main
git pull origin main
git checkout -b release/v0.1.0
git merge dev
git push -u origin release/v0.1.0
```

Then open a PR:

```text
base: main
compare: release/v0.1.0
```

Why:

- `release/v0.1.0` becomes a stabilization branch.
- Only release fixes should go into it.
- After it is merged into `main`, tag the release.

Tag a release from `main`:

```bash
git checkout main
git pull origin main
git tag v0.1.0
git push origin v0.1.0
```

Why:

- A tag marks an exact production version.
- Tags are useful for changelogs, release notes, and deployment history.

#### Q. Should I cherry-pick feature commits into `main`?

Usually no.

Cherry-picking is useful as an exception, not the normal workflow.

Use cherry-pick when:

- one urgent bugfix from `dev` must go to `main`
- a branch contains too much unrelated work
- you need one specific commit without merging the whole branch

Command:

```bash
git checkout main
git pull origin main
git cherry-pick <commit-hash>
git push origin main
```

Why:

- `git cherry-pick` copies one commit onto the current branch.
- It is powerful but can create duplicate commits and messy history if overused.
- For normal feature delivery, prefer PRs and merges.

#### Q. What is the best workflow for this project today?

Use this:

```text
feat/utils -> dev
feat/tools -> dev
feat/agents-and-chains -> dev
feat/pipeline -> dev
dev -> main
```

Why:

- Each feature stays understandable.
- `dev` proves the pieces work together.
- `main` stays stable.
- The GitHub history tells a clear engineering story.

---

## Continuous Integration CI

#### Q. What is CI?

CI means:

```text
Continuous Integration
```

Continuous Integration (CI) is a software development practice where code changes are automatically built, tested, and validated upon every commit or pull request to a shared repository. The goal is to detect integration errors early by maintaining a single source of truth and ensuring all changes pass a defined quality gate, typically linting, unit tests, and type checks, before being merged. CI is the first half of the CI/CD pipeline, with CD (Continuous Delivery/Deployment) handling automated release to staging or production environments.

In this project, CI runs on GitHub Actions.

Why:

- It catches broken code before it reaches `main`.
- It makes every branch follow the same quality gate.
- It gives reviewers confidence that the project installs, lints, type-checks, and tests cleanly.
- It is industry standard because teams cannot rely only on "it works on my machine."

The idea:

```text
developer pushes code -> GitHub Actions starts -> install dependencies -> run checks -> pass/fail result
```

#### Q. What file defines CI in this project?

The CI workflow file is:

```text
.github/workflows/ci.yml
```

Why this path:

- GitHub Actions automatically looks inside `.github/workflows/`.
- Any `.yml` or `.yaml` file in that folder can define a workflow.

#### Q. Is it `.yaml` or `.yml`?

Both are valid YAML file extensions:

```text
ci.yml
ci.yaml
```

GitHub Actions accepts both.

In this project:

```text
.github/workflows/ci.yml
```

Why:

- `.yml` is very common for GitHub Actions workflows.
- `.yaml` is also correct.
- The content matters more than the extension, as long as it is valid YAML.

For pre-commit, the convention is:

```text
.pre-commit-config.yaml
```

Why:

- That filename is what people expect when using `pre-commit`.
- It is the standard name shown in the pre-commit documentation and examples.

#### Q. What does the CI YAML file do?

Current workflow:

```yaml
name: CI

"on":
  push:
    branches:
      - main
      - dev
      - "feat/**"
  pull_request:
    branches:
      - main
      - dev

jobs:
  test:
    name: Test and quality checks
    runs-on: ubuntu-latest

    env:
      OPENAI_API_KEY: test-openai-key
      TAVILY_API_KEY: test-tavily-key

    steps:
      - name: Checkout repository
        uses: actions/checkout@v5

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --locked --all-groups

      - name: Lint
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy src

      - name: Test with coverage
        run: uv run pytest --cov --cov-report=term-missing
```

What each part means:

```yaml
name: CI
```

Why:

- This is the workflow name shown in GitHub Actions.

```yaml
"on":
```

Why:

- This defines when the workflow runs.
- It is quoted because YAML parsers can sometimes treat `on` as a boolean-like keyword depending on YAML version/tooling.
- Quoting it avoids ambiguity.

```yaml
push:
  branches:
    - main
    - dev
    - "feat/**"
```

Why:

- CI runs when code is pushed to `main`.
- CI runs when integrated development code is pushed to `dev`.
- CI runs when feature branches like `feat/tools` or `feat/pipeline` are pushed.

```yaml
pull_request:
  branches:
    - main
    - dev
```

Why:

- CI runs when opening PRs into `dev`.
- CI runs when opening PRs into `main`.
- This supports the workflow:

```text
feat/* -> dev -> main
```

```yaml
runs-on: ubuntu-latest
```

Why:

- GitHub provides a clean Linux machine for the job.
- Linux CI is common, fast, and reliable for Python projects.
- It proves the project can run outside your Windows laptop.

```yaml
env:
  OPENAI_API_KEY: test-openai-key
  TAVILY_API_KEY: test-tavily-key
```

Why:

- Some imports or configuration may expect these environment variables.
- CI should not use real secrets for mocked tests.
- Tests should mock external APIs unless they are explicitly integration tests that require live services.

```yaml
uses: actions/checkout@v5
```

Why:

- This downloads the repository code into the GitHub Actions runner.
- Without checkout, the runner has no project files.

```yaml
uses: astral-sh/setup-uv@v7
```

Why:

- This installs uv in the CI environment.
- It also supports uv caching, making future CI runs faster.

```yaml
run: uv python install 3.12
```

Why:

- This ensures Python 3.12 is available.
- It matches the local project setup.

```yaml
run: uv sync --locked --all-groups
```

Why:

- `uv sync` installs dependencies.
- `--locked` makes CI use `uv.lock` exactly and fail if the lockfile is outdated.
- `--all-groups` installs development tools such as pytest, pytest-cov, ruff, mypy, and pre-commit dependencies.
- This is important because CI should be reproducible.

```yaml
run: uv run ruff check .
```

Why:

- Runs lint checks.
- Catches unused imports, bad import ordering, common bug patterns, and style issues.

```yaml
run: uv run mypy src
```

Why:

- Runs static type checking on the application source code.
- Catches type errors before runtime.

```yaml
run: uv run pytest --cov --cov-report=term-missing
```

Why:

- Runs the test suite.
- Measures test coverage.
- Shows exactly which lines are not covered.

#### Q. What commands should I run locally before pushing?

Run these from the project root:

```bash
uv sync
uv run ruff check .
uv run mypy src
uv run pytest --cov --cov-report=term-missing
```

On Windows, if uv has TLS issues:

```bash
uv sync --native-tls
```

Why:

- These commands match the CI checks.
- If they pass locally, CI is more likely to pass on GitHub.

#### Q. Why do industry teams use CI?

Industry teams use CI because:

- many people work on the same codebase
- code changes can break unrelated parts of the system
- reviewers need automated proof that basic quality checks passed
- production branches must stay stable
- manual testing alone is too slow and unreliable

In this project, CI supports the branching strategy:

```text
feat/* -> dev -> main
```

Feature branches can break while being developed, but before they merge into `dev` or `main`, CI should prove they are healthy.

---

## Pre-Commit Hooks

#### Q. What are pre-commit hooks?

Pre-commit hooks are automated validation scripts that execute locally before Git finalizes a commit. They enforce repository standards such as formatting, linting, static analysis, secret checks, file-size checks, and metadata validation at the earliest possible point in the development workflow.

They act as a local quality gate:

```text
git commit -> pre-commit hooks run -> checks pass -> commit is created
```

If checks fail:

```text
git commit -> hooks fail -> fix files -> git add again -> commit again
```

Why:

- CI catches issues after pushing.
- Pre-commit catches issues before pushing.
- This reduces failed CI runs by catching simple problems locally.
- It keeps formatting and repository hygiene consistent across contributors.
- It prevents avoidable review comments about whitespace, imports, line endings, or formatting.
- It supports professional team workflows where code quality rules are enforced consistently.

#### Q. What file configures pre-commit in this project?

The config file is:

```text
.pre-commit-config.yaml
```

Why:

- This file tells pre-commit which hooks to install and run.
- It is committed to the repo so every developer can use the same checks.

#### Q. How do I install pre-commit for this project?

Step 1: Make sure dev dependencies are installed.

```bash
uv sync
```

Why:

- `pre-commit` is a dev dependency in `pyproject.toml`.
- `uv sync` installs it into `.venv/`.

Step 2: Install the Git hook.

```bash
uv run pre-commit install
```

Alternative if `.venv` is activated:

```bash
pre-commit install
```

Why:

- This writes a hook file into:

```text
.git/hooks/pre-commit
```

- `.git/hooks/pre-commit` is local to your machine.
- It is not committed to Git.
- Every new machine must run `pre-commit install` once.

#### Q. How do I run pre-commit manually?

Run all hooks on all files:

```bash
uv run pre-commit run --all-files
```

Run only changed files during commit:

```bash
git commit -m "your message"
```

Why:

- `pre-commit run --all-files` is useful after setting up hooks or changing config.
- Normal commits only check the relevant files, which is faster.

#### Q. What hooks are configured?

Current hooks:

```text
trailing-whitespace
end-of-file-fixer
check-yaml
check-toml
check-added-large-files
mixed-line-ending
ruff-check
ruff-format
mypy
```

Why each exists:

```text
trailing-whitespace
```

- removes useless spaces at line ends
- prevents noisy diffs

```text
end-of-file-fixer
```

- ensures files end with one newline
- avoids formatting inconsistencies across editors

```text
check-yaml
```

- validates YAML syntax
- important for GitHub Actions and pre-commit config files

```text
check-toml
```

- validates TOML syntax
- important for `pyproject.toml`

```text
check-added-large-files
```

- prevents accidentally committing large files
- useful for avoiding datasets, model files, logs, and generated artifacts

```text
mixed-line-ending
```

- normalizes line endings
- important because this project is developed on Windows but CI runs on Linux

```text
ruff-check
```

- runs fast linting
- catches unused imports, import sorting issues, and common Python mistakes

```text
ruff-format
```

- formats code consistently
- replaces the need to argue about style manually

```text
mypy
```

- checks types
- helps catch mistakes before runtime

#### Q. Which branches do pre-commit hooks affect?

Pre-commit affects the branch you are committing on locally.

Examples:

```text
commit on feat/tools -> hooks run on feat/tools
commit on dev -> hooks run on dev
commit on main -> hooks run on main
```

Why:

- Hooks are local Git behavior.
- They do not belong to one branch.
- They run whenever you commit in this repository after installation.

Important:

- `.pre-commit-config.yaml` is committed.
- `.git/hooks/pre-commit` is not committed.
- On a new machine, run:

```bash
uv sync
uv run pre-commit install
```

#### Q. What should I do when pre-commit modifies files?

Sometimes hooks automatically fix files.

Example:

```text
trim trailing whitespace........Failed
- files were modified by this hook
```

Then run:

```bash
git status
git add <fixed-files>
git commit -m "your message"
```

Why:

- Pre-commit changed files to make them compliant.
- You must stage those changes before committing.

#### Q. Why do industry teams use pre-commit?

Industry teams use pre-commit because:

- it shifts quality checks earlier
- it reduces CI failures
- it keeps formatting consistent
- it avoids review comments about whitespace and imports
- it helps developers catch mistakes before pushing

The professional workflow is:

```text
pre-commit catches local issues
CI confirms the repo works in a clean remote environment
PR review checks architecture and business logic
```

---

## Testing Strategy

#### Q. What is software testing?

Software testing is the practice of verifying that code behaves as expected under defined conditions. In professional engineering workflows, tests act as executable specifications: they document expected behavior, protect against regressions, and provide confidence that changes can be integrated safely.

In this project, tests are used to verify:

- individual tool behavior
- pipeline orchestration
- mocked external API interactions
- import safety
- baseline code quality through coverage

Why:

- Agentic AI systems depend on multiple moving parts: LLMs, tools, search APIs, scraping, chains, and orchestration logic.
- Testing protects the deterministic engineering layer around the non-deterministic AI layer.
- Industry teams use tests to make refactoring safer and to prevent production regressions.

#### Q. What tests were added for the current code?

Current test files:

```text
tests/conftest.py
tests/test_tools.py
tests/test_research_pipeline.py
```

What they cover:

```text
test_tools.py
```

- tests `web_search`
- tests `scrape_url`
- mocks Tavily
- mocks network requests
- avoids real API calls

```text
test_research_pipeline.py
```

- tests the pipeline orchestration
- mocks search agent
- mocks research agent
- mocks writer chain
- mocks critic chain
- verifies data moves through the workflow correctly

```text
conftest.py
```

- sets test environment variables
- prevents imports from failing because API keys are missing

#### Q. Why do we mock OpenAI, Tavily, and network calls in tests?

Mocks are controlled replacements for real dependencies. They allow tests to simulate external systems such as OpenAI, Tavily, HTTP requests, databases, or file systems without actually calling those services.

Normal CI tests should be deterministic:

```text
same code + same test inputs -> same test result
```

Mocked tests avoid:

- API costs
- rate limits
- internet failures
- flaky search results
- changing web pages
- secret leakage
- slow test runs

Why industry teams do this:

- CI must be reliable.
- Tests should fail because code is broken, not because a website is down.
- External-service tests are useful, but they should be separated from normal unit tests.
- Mocked tests are cheaper, faster, safer, and easier to debug.
- Live-service tests are usually run separately as scheduled checks, staging checks, or explicit integration tests.

#### Q. How do I run all tests?

Command:

```bash
uv run pytest
```

Why:

- Runs all tests discovered under `tests/`.
- Uses the uv-managed project environment.

#### Q. How do I run tests with coverage?

Command:

```bash
uv run pytest --cov --cov-report=term-missing
```

Why:

- `--cov` measures how much application code tests execute.
- `--cov-report=term-missing` shows which lines are not covered.

Current coverage threshold in `pyproject.toml`:

```text
fail_under = 40
```

Why:

- This project is early.
- A realistic early threshold prevents fake-strict CI.
- As the project matures, raise the threshold.

Suggested future targets:

```text
early prototype: 40-60%
serious portfolio project: 70-80%
production-critical code: 80-90%+
```

#### Q. How do I run only unit tests?

Current unit-style tests:

```bash
uv run pytest tests/test_tools.py
```

Why:

- These tests isolate individual tools.
- They are fast.
- They mock external dependencies.

#### Q. How do I run integration-style tests?

Current integration-style test:

```bash
uv run pytest tests/test_research_pipeline.py
```

Why:

- It checks multiple components working together.
- It verifies the pipeline passes state from search to scrape to writer to critic.
- It still mocks LLM/API calls so it can run safely in CI.

#### Q. What is the difference between unit, integration, and end-to-end tests?

Unit tests:

```text
Tests that verify one small function, class, or module in isolation.
```

Example:

```text
web_search formats Tavily results correctly
```

Why:

- They are fast.
- They are precise.
- They are easy to debug.
- They help identify exactly which unit of logic broke.

Integration tests:

```text
Tests that verify multiple components working together through their real interfaces.
```

Example:

```text
research pipeline calls agents and chains in the right order
```

Why:

- They catch wiring problems between modules.
- They prove components cooperate correctly.
- They are especially important in agentic systems where tools, agents, chains, and state must pass data correctly.

End-to-end tests:

```text
Tests that verify the system from the user's perspective across the full application path.
```

Example future tests:

```text
run API endpoint -> trigger agent workflow -> receive final report
open Streamlit UI -> submit query -> see result
```

Why:

- They are closest to real user behavior.
- They validate that the whole system works together.
- They are slower and more fragile than unit tests.
- Teams usually maintain fewer end-to-end tests than unit or integration tests.

#### Q. Do tests change when code changes?

Yes.

Tests are living documentation of expected behavior.

When code behavior changes intentionally:

```text
update the code
update the tests
run the test suite
commit both together
```

Why:

- Tests should describe what the system is supposed to do now.
- Old tests may become incorrect if the intended behavior changed.

#### Q. Can test updates be automated?

Running tests can be automated.

Writing meaningful tests cannot be fully automated.

Automated:

- CI runs tests on push and PR
- coverage is calculated automatically
- lint/type checks run automatically
- pre-commit runs local checks before commit

Not fully automated:

- deciding expected behavior
- designing good assertions
- deciding what should be mocked
- deciding what should be a unit vs integration test

Why:

- Tests are engineering judgment.
- Tools can execute tests, but humans define what correctness means.

#### Q. What testing setup is Munich/industry-ready for Agentic AI projects?

A strong Agentic AI testing strategy should include:

```text
unit tests
integration tests
end-to-end tests
mocked LLM tests
retrieval quality tests
prompt regression tests
evaluation datasets
latency checks
cost checks
observability checks
```

For this project, the next test layers should be:

1. Tool tests

```text
web search, scraping, parsing, caching, retries
```

2. Pipeline/graph tests

```text
agent orchestration, routing, state transitions, fallback paths
```

3. Retrieval tests

```text
chunking, vector search, reranking, citation coverage
```

4. Evaluation tests

```text
does the report cite sources?
does it avoid unsupported claims?
does it meet quality thresholds?
```

5. API/UI smoke tests

```text
FastAPI starts
Streamlit page loads
basic user flow works
```

Why industry teams care:

- Agentic systems can fail silently.
- LLM outputs vary.
- External tools fail.
- Search results change.
- Retrieval can return irrelevant context.
- CI tests protect basic engineering correctness.
- Evaluation pipelines protect AI output quality.

#### Q. What are the main local quality commands for this project?

Install/sync dependencies:

```bash
uv sync
```

Run lint:

```bash
uv run ruff check .
```

Run formatter:

```bash
uv run ruff format .
```

Run type checking:

```bash
uv run mypy src
```

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov --cov-report=term-missing
```

Run pre-commit hooks:

```bash
uv run pre-commit run --all-files
```

Run compile check:

```bash
uv run python -m compileall src main.py ui
```

Why:

- These commands cover installability, syntax, formatting, linting, typing, tests, and coverage.
- Together, they form the local equivalent of CI.
