from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from git import Repo

import os


app = FastAPI()


# ============================================================
# CLONE REPOSITORY
# ============================================================

@app.post("/clone")
def clone_repository(github: str):

    # Get repository name
    repository_name = github.rstrip("/").split("/")[-1]

    # Remove .git
    repository_name = repository_name.replace(".git", "")

    # Absolute path of cloned repository
    repository_path = os.path.abspath(repository_name)

    # --------------------------------------------------------
    # Repository already exists
    # --------------------------------------------------------

    if os.path.exists(repository_path):

        return {
            "message": "Directory already exists",
            "directory": repository_name,
            "files": get_files(repository_path)
        }

    # --------------------------------------------------------
    # Clone repository
    # --------------------------------------------------------

    try:

        Repo.clone_from(
            github,
            repository_path
        )

    except Exception as error:

        return {
            "error": str(error)
        }

    # --------------------------------------------------------
    # Get files
    # --------------------------------------------------------

    return {
        "message": "Repository cloned successfully",
        "directory": repository_name,
        "files": get_files(repository_path)
    }


# ============================================================
# GET FILE LIST
# ============================================================

def get_files(directory):

    files = []

    for root, dirs, filenames in os.walk(directory):

        # Don't show .git
        dirs[:] = [
            directory_name
            for directory_name in dirs
            if directory_name != ".git"
        ]

        for filename in filenames:

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                directory
            )

            # Convert Windows \ to /
            relative_path = relative_path.replace(
                os.sep,
                "/"
            )

            files.append(relative_path)

    return sorted(files)


# ============================================================
# READ FILE
# ============================================================

@app.get("/file")
def get_file(
    repository: str,
    path: str
):

    repository_path = os.path.abspath(repository)

    file_path = os.path.abspath(
        os.path.join(
            repository_path,
            path
        )
    )

    # --------------------------------------------------------
    # Security check
    # Prevent reading files outside repository
    # --------------------------------------------------------

    if not file_path.startswith(
        repository_path + os.sep
    ):

        return {
            "error": "Invalid file path"
        }

    if not os.path.isfile(file_path):

        return {
            "error": "File not found"
        }

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            code = file.read()

        return {
            "file": path,
            "code": code
        }

    except Exception as error:

        return {
            "error": str(error)
        }


# ============================================================
# SAVE FILE
# ============================================================

@app.put("/file")
def save_file(
    repository: str,
    path: str,
    code: str = Body(...)
):

    repository_path = os.path.abspath(repository)

    file_path = os.path.abspath(
        os.path.join(
            repository_path,
            path
        )
    )

    # --------------------------------------------------------
    # Security check
    # --------------------------------------------------------

    if not file_path.startswith(
        repository_path + os.sep
    ):

        return {
            "error": "Invalid file path"
        }

    if not os.path.isfile(file_path):

        return {
            "error": "File not found"
        }

    try:

        # Write modified code to local file
        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(code)

        return {
            "message": "File saved successfully",
            "file": path
        }

    except Exception as error:

        return {
            "error": str(error)
        }


# ============================================================
# SERVE FRONTEND
# ============================================================

app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
) 