import os
import subprocess

import dotenv
import requests

import nox
from nox import command
import dotenv


PYTHON_VERSIONS = [os.getenv("PYTHON_VERSIONS")]

def check_if_commited() -> bool:
    """returns if the current branch is commited

    Returns:
        bool: status of branch
    """
    # Change the working directory
    # Run the git status command and capture the output
    result = subprocess.run(["git", "status"], capture_output=True, text=True)

    # Get the output of the command
    output = result.stdout
    print(output)
    # Check if the output contains any indications of uncommitted files
    if (
        "Changes not staged for commit" in output
        or "Untracked files" in output
        or "aucune modification n'a été ajoutée à la validation" in output
        or "modifié :" in output
    ):
        return False
    else:
        return True


# Define the necessary headers and data
def create_github_pages(i: int =0) -> None:
    if i < 2:
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
        else:
            print("Failed to create GitHub Pages.")
            print("Status code:", response.status_code)
            print("Error message:", response.json())
            create_github_pages(i+1)
    else:
        pass


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
        session.run("git", "push")


def list_sub_folder(folder) -> list:
    # find all folder in the folder
    sub_folder = []
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isdir(path) and "__pycache__" not in path:
            sub_folder.append(path)
            sub_folder.extend(list_sub_folder(path))
    return sub_folder


def connect_branch(name: str, session: nox.Session) -> bool:
    """connect to a branch if it exists or create it

    Args:
        name (str): name of the b ranch
        session (nox.Session): session nox running

    Returns:
        bool: return if the cheeckout was successful
    """
    if check_if_commited():
        try:
            session.run("git", "rev-parse", "--verify", name, silent=True)
        except command.CommandFailed:
            print(f"La branche {name} n'existe pas. Création de la branche...")
            session.run("git", "branch", name)
        else:
            print(f"La branche {name} existe déjà.")
        session.run("git", "checkout", name)
        return True
    return False


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
    if check_if_commited():
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
    else:
        print("Please commit your files before formatting")


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def dev(session: nox.Session) -> None:
    """_summary_

    Args:
        session (nox.Session): _description_
    """
    session.install(
        "-r", "requirements/dev-requirements.txt"
    )  # installe les dependances
    if check_if_commited():
        connect_branch("dev", session)
    else:
        print("Please commit your files before formatting")


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    branch = "build"
    if connect_branch(branch, session):
        session.install("-r", "requirements/test-requirements.txt")
        try:
            test = session.run("python", "-u", "test/main_test.py")
        except:
            print("test failed")
        # check if ll test passed well
        commit_and_push_file(branch, session)
    else:
        print("Please commit your files before testing")


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def docs(session: nox.Session) -> None:
    try:
        branch = "docs"
        if connect_branch("main", session):
            session.install("-r", "requirements/docs-requirements.txt")
            nb_elements_in_source = os.listdir("./doc/source")
            session.run(
                "sphinx-apidoc",
                "--implicit-namespaces",
                "-o",
                "./doc/source",
                "./src",
                "./noxfile.py",
                "./test",
                "./__pycache__",
            )
            if len(nb_elements_in_source) == os.listdir("./doc/source"):
                session.run("git", "add", "-f", "doc/source")
                session.run("git", "commit", "-m", "docs")
            try:
                session.run("git", "branch", "-D", "docs")
                session.run("git", "push", "origin", "--delete", "docs")
            except:
                print("branch does not exist in github")
            # recreate branch
            connect_branch(branch, session)
            session.run("git", "update-index", "--assume-unchanged", ".env")
            session.run("sphinx-build", "-b", "html", "./doc/source", "./docs")
            session.run("touch", "docs/.nojekyll")
            commit_and_push_file(branch, session)
            session.run("git", "checkout", "main")
            create_github_pages()
        else:
            print("Please commit your files before formatting")
    except:
        connect_branch("main", session)

@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    session.install("-r", "requirements/lint-requirements.txt")
    # session.run("pylint", "noxfile.py")


@nox.session(venv_backend="virtualenv", python=PYTHON_VERSIONS)
def build(session: nox.Session) -> None:
    session.install("-r", "requirements/build-requirements.txt")
    if check_if_commited():
        connect_branch("main", session)
    else:
        print("Please commit your files before formatting")
