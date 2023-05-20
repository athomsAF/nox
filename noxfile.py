import os
import subprocess

import dotenv
import requests

import nox
from nox import command

PYTHON_VERSIONS = ["3.11"]


def check_if_commited() -> bool:
    # Change the working directory
    # Run the git status command and capture the output
    result = subprocess.run(["git", "status"], capture_output=True, text=True)

    # Get the output of the command
    output = result.stdout
    print(output)
    # Check if the output contains any indications of uncommitted files
    if "Changes not staged for commit" in output or "Untracked files" in output:
        return (False)
    else:
        return (True)


# Define the necessary headers and data
def create_github_pages() -> None:
    dotenv.load_dotenv()
    TOKEN = os.getenv("GITHUB_TOKEN")
    USER = os.getenv("GITHUB_USER")
    REPOSITORY = os.getenv("GITHUB_REPOSITORY")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {"source": {"branch": "docs", "path": "/docs"}}
    # Make the POST request
    response = requests.post(
        f"https://api.github.com/repos/{USER}/{REPOSITORY}/pages",
        headers=headers,
        json=data,
    )
    # Check the response status
    if response.status_code == 201:
        print("GitHub Pages send successfully!")
        response = requests.post(
            "https://api.github.com/repos/OWNER/REPO/pages", headers=headers, json=data
        )
        if response.status_code == 201:
            print("GitHub Pages created successfully!")
    else:
        print("Failed to create GitHub Pages.")
        print("Status code:", response.status_code)
        print("Error message:", response.json())


def commit_and_push_file(branch: str, session) -> None:
    time = session.run("date", "+%Y-%m-%d-%H-%M")
    if branch == "test" or branch == "build":
        session.run("git", "add", "test")
        session.run("git", "add", "main.py")
        session.run("git", "add", "build")
        # create a commit ith the date as YYY-MM-DD-HH-mm
        time = session.run("date", "+%Y-%m-%d-%H-%M")
        session.run("git", "push", "origin", "build")
    elif branch == "docs":
        session.run("git", "rm", "-r", "*")
        session.run("git", "add", "docs")
        session.run("git", "commit", "-m", "docs")
        session.run("git", "push", "origin", "docs")
    elif branch == "format":
        session.run("git", "add", ".")
        session.run("git", "commit", "-m", f"format - {time}")
        session.run("git","push")


def find_children_files(directory) -> list:
    # find all folder in the directory
    return [
        f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))
    ]


def connect_branch(name: str, session: nox.Session) -> None:
    try:
        session.run("git", "rev-parse", "--verify", name, silent=True)
    except command.CommandFailed:
        print(f"La branche {name} n'existe pas. Création de la branche...")
        session.run("git", "branch", name)
    else:
        print(f"La branche {name} existe déjà.")

    print(f"Se connecter à la branche {name}..")
    session.run("git", "checkout", name)


@nox.session(
    venv_backend="virtualenv", python=PYTHON_VERSIONS
)  # use this annotation on the wrapper works like a charm
def format(session: nox.Session) -> None:
    """
    format session uising black pylint and flake8
    Parameters
    ----------
    session : nox_session
    """
    connect_branch("main", session)
    session.install(
        "-r", "requirements/format-requirements.txt"
    )  # installe les dependances
    try:
        session.run("black", "--exclude", ".nox", ".")  # formate le code
        session.run("isort", ".")  # formate les imports
        commit_and_push_file("format", session)
    except:
        print("formatting failed")
    if check_if_commited():
        print("formatting done")
    else:
        print("formatting failed")


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def dev(session: nox.Session) -> None:
    """_summary_

    Args:
        session (nox.Session): _description_
    """
    session.install(
        "-r", "requirements/dev-requirements.txt"
    )  # installe les dependances
    # session.install("-e", ".") #reccupere la derniere version
    # créer un setup.py ou pyproject.tomel ==> metadata du projet empàlacement du readme ect


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    branch = "build"
    connect_branch(branch, session)
    session.install("-r", "requirements/test-requirements.txt")
    try:
        test = session.run("python", "-u", "test/main_test.py")
    except:
        print("test failed")
    # check if ll test passed well
    commit_and_push_file(branch, session)


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def docs(session: nox.Session) -> None:
    branch = "docs"
    connect_branch("main", session)
    # delete branch if it exists
    try:
        session.run("git", "branch", "-D", "docs")
        session.run("git", "push", "origin", "--delete", "docs")
    except:
        print("branch does not exist in github")
    # recreate branch
    connect_branch(branch, session)
    session.run("git", "update-index", "--assume-unchanged", ".env")
    session.install("-r", "requirements/docs-requirements.txt")
    for i in find_children_files("program"):
        session.run(
            "sphinx-apidoc",
            "-o",
            "./docs_information/source",
            i,
            "./noxfile.py",
            "./test",
        )
    session.run(
        "sphinx-apidoc",
        "-o",
        "./docs_information/source",
        "./",
        "./noxfile.py",
        "./test",
    )
    session.run("sphinx-build", "-b", "html", "./docs_information/source", "./docs")
    session.run("touch", "docs/.nojekyll")
    commit_and_push_file(branch, session)
    session.run("git", "checkout", "main")
    create_github_pages()


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    session.install("-r", "requirements/lint-requirements.txt")
    # session.run("pylint", "noxfile.py")


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def build(session: nox.Session) -> None:
    session.install("-r", "requirements/requirements.txt")
