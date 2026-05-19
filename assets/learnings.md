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
