from pathlib import Path

# CURRENT PROJECT DIRECTORY
# "." means the folder where this script is being run.
project_path = Path(".")

# FOLDERS
folders = [
    "rag",
    "eval",
    "tests",
]


# FILES
files = [
    "rag/__init__.py",
    "rag/embedding.py",
    "rag/chat_model.py",

    "eval/__init__.py",
    "eval/test_queries.py",

    "tests/__init__.py",
    "tests/test_connection.py",
    
    "README.md",
    "requirements.txt",
    ".env.example",
    ".env",
    ".gitignore",
]

# CREATE FOLDERS
for folder in folders:
    folder_path = project_path / folder
    folder_path.mkdir(
        exist_ok=True
    )

# CREATE FILES
for file in files:
    file_path = project_path / file
    file_path.touch(
        exist_ok=True
    )


# SUCCESS MESSAGE
print("\nProject structure created successfully!\n")
print("Project location:")
print(project_path.resolve())