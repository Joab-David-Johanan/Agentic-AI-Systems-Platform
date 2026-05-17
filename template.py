"""
templates.py — Multi-Agent Research System scaffold manager

Usage:
    python templates.py            # interactive menu
    python templates.py scaffold   # mode 1: create project structure
    python templates.py teardown   # mode 2: remove scaffolded structure
    python templates.py sync       # mode 3: scan files and embed into this script
"""

import os
import sys
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG = "research_system"

FOLDERS = [
    f"src/{PKG}/agents",
    f"src/{PKG}/tools",
    f"src/{PKG}/chains",
    f"src/{PKG}/config",
    f"src/{PKG}/utils",
    "ui",
    "tests",
    "outputs",
]

INITS = [
    f"src/{PKG}/__init__.py",
    f"src/{PKG}/agents/__init__.py",
    f"src/{PKG}/tools/__init__.py",
    f"src/{PKG}/chains/__init__.py",
    f"src/{PKG}/config/__init__.py",
    f"src/{PKG}/utils/__init__.py",
    "ui/__init__.py",
    "tests/__init__.py",
]

# Entire directories removed by teardown
TEARDOWN_DIRS = ["src", "ui", "tests", "outputs"]

# Root-level files removed by teardown
TEARDOWN_FILES = ["pyproject.toml", ".env.example", ".env"]

# What sync scans
SYNC_SCAN_DIRS = [f"src/{PKG}", "ui", "tests"]
SYNC_SCAN_ROOT_FILES = ["pyproject.toml", ".env.example", "main.py"]
SYNC_SKIP_DIRS = {"__pycache__", ".git", "outputs", "assets"}
SYNC_SKIP_FILES = {
    "templates.py",
    ".env",
    "requirements.txt",
    "README.md",
    "LICENSE",
    ".gitignore",
}

# <<<SYNC_START>>>
FILES = {
    ".env": "OPENAI_API_KEY=\nTAVILY_API_KEY=\nMODEL_NAME=gpt-4o-mini\n",
    ".env.example": "OPENAI_API_KEY=\nTAVILY_API_KEY=\nMODEL_NAME=gpt-4o-mini\n",
    "outputs/.gitkeep": "",
    "pyproject.toml": (
        "[build-system]\n"
        'requires = ["setuptools>=61", "wheel"]\n'
        'build-backend = "setuptools.build_meta"\n'
        "\n"
        "[project]\n"
        'name = "research_system"\n'
        'version = "0.1.0"\n'
        'description = "Multi-Agent Research System"\n'
        'requires-python = ">=3.10"\n'
        "dependencies = [\n"
        '    "langchain>=0.2.0",\n'
        '    "langchain-core>=0.2.0",\n'
        '    "langchain-community>=0.2.0",\n'
        '    "langchain-openai>=0.1.0",\n'
        '    "streamlit>=1.0.0",\n'
        '    "tavily-python>=0.3.0",\n'
        '    "beautifulsoup4>=4.12.0",\n'
        '    "readability-lxml",\n'
        '    "trafilatura",\n'
        '    "requests>=2.31.0",\n'
        '    "lxml>=5.0.0",\n'
        '    "python-dotenv>=1.0.0",\n'
        '    "rich>=13.7.0",\n'
        "]\n"
        "\n"
        "[tool.setuptools.packages.find]\n"
        'where = ["src"]\n'
    ),
}
# <<<SYNC_END>>>


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _abs(path: str) -> str:
    return os.path.join(ROOT, path)


def _write(path: str, content: str = "") -> None:
    full = _abs(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if os.path.exists(full):
        print(f"  skip   {path}")
        return
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  create {path}")


def _mkdir(path: str) -> None:
    os.makedirs(_abs(path), exist_ok=True)
    print(f"  mkdir  {path}")


# ---------------------------------------------------------------------------
# Mode 1 — scaffold
# ---------------------------------------------------------------------------


def scaffold() -> None:
    print("Scaffolding project...\n")
    for folder in FOLDERS:
        _mkdir(folder)
    for init in INITS:
        _write(init)
    for path, content in FILES.items():
        _write(path, content)
    print("\nDone.")
    print("  1. Fill in .env with your API keys")
    print("  2. pip install -e .")


# ---------------------------------------------------------------------------
# Mode 2 — teardown
# ---------------------------------------------------------------------------


def teardown() -> None:
    answer = input(
        "Delete all scaffolded files and folders? Type 'yes' to confirm: "
    ).strip()
    if answer != "yes":
        print("Aborted.")
        return

    print("\nRemoving scaffolded structure...\n")
    for d in TEARDOWN_DIRS:
        full = _abs(d)
        if os.path.isdir(full):
            shutil.rmtree(full)
            print(f"  removed {d}/")
        else:
            print(f"  missing {d}/")

    for f in TEARDOWN_FILES:
        full = _abs(f)
        if os.path.isfile(full):
            os.remove(full)
            print(f"  removed {f}")
        else:
            print(f"  missing {f}")

    print("\nDone. Run scaffold to start fresh.")


# ---------------------------------------------------------------------------
# Mode 3 — sync
# ---------------------------------------------------------------------------


def sync() -> None:
    print("Scanning project files...\n")
    scanned: dict[str, str] = {}

    for scan_dir in SYNC_SCAN_DIRS:
        abs_dir = _abs(scan_dir)
        if not os.path.isdir(abs_dir):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_dir):
            dirnames[:] = [d for d in dirnames if d not in SYNC_SKIP_DIRS]
            for fname in filenames:
                if fname in SYNC_SKIP_FILES:
                    continue
                abs_file = os.path.join(dirpath, fname)
                rel = os.path.relpath(abs_file, ROOT).replace("\\", "/")
                with open(abs_file, encoding="utf-8", errors="replace") as fh:
                    scanned[rel] = fh.read()
                print(f"  scan   {rel}")

    for fname in SYNC_SCAN_ROOT_FILES:
        abs_file = _abs(fname)
        if os.path.isfile(abs_file):
            with open(abs_file, encoding="utf-8", errors="replace") as fh:
                scanned[fname] = fh.read()
            print(f"  scan   {fname}")

    # Always carry forward these entries even if not on disk
    for key in (".env.example", ".env", "outputs/.gitkeep"):
        if key not in scanned:
            scanned[key] = FILES.get(key, "")

    # Build the replacement block
    lines = ["# <<<SYNC_START>>>\n", "FILES = {\n"]
    for path, content in sorted(scanned.items()):
        lines.append(f"    {repr(path)}: {repr(content)},\n")
    lines.append("}\n")
    lines.append("# <<<SYNC_END>>>")

    script_path = _abs("templates.py")
    with open(script_path, encoding="utf-8") as fh:
        original = fh.read()

    start = original.index("# <<<SYNC_START>>>")
    end = original.index("# <<<SYNC_END>>>") + len("# <<<SYNC_END>>>")
    updated = original[:start] + "".join(lines) + original[end:]

    with open(script_path, "w", encoding="utf-8") as fh:
        fh.write(updated)

    print(f"\nEmbedded {len(scanned)} files into templates.py.")
    print("Run scaffold on a clean directory to recreate this exact structure.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _menu() -> str:
    print("\n")
    print("Multi-Agent Research System — templates.py\n")
    print("  1. scaffold  — create project structure")
    print("  2. teardown  — remove scaffolded structure")
    print("  3. sync      — scan current files and embed into this script")
    return input("\nSelect mode (1/2/3): ").strip()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else _menu()
    dispatch = {
        "1": scaffold,
        "scaffold": scaffold,
        "2": teardown,
        "teardown": teardown,
        "3": sync,
        "sync": sync,
    }
    fn = dispatch.get(mode)
    if fn is None:
        print(f"Unknown mode: {mode!r}. Use 1, 2, or 3.")
        sys.exit(1)
    fn()


if __name__ == "__main__":
    main()
