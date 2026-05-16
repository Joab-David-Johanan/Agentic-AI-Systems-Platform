# Steps taken to implement the project

#### 1. Environment creation

```bash
conda create -n agent-env python=3.11
```

```bash
conda activate agent-env
```

create a requirements.txt with all the packages that you need

```bash
pip install -r requirements.txt
```

***`Environment creation`***-->***`Environment activation`***-->***`Install requirements.txt`***

#### 2. Create Project template and pyproject.toml file

- Here we create a `template.py` file in the project root directory that defines our project structure.
- Ensure the `pyproject.toml` file is created only after the project structure is setup as it uses editable install to add `src/` to sys.path thus making our package `research_system` importable from anywhere in our project. The pyproject.toml file also installs the required dependencies.
- Run the `pip install -e .` command after the `project.toml` file is created to allow editable install.

***`template.py`***-->***`pyproject.toml`***-->***`pip install -e .`***