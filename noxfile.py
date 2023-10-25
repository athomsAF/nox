import nox

PYTHON_VERSIONS = ["3.11"]
env = 'virtualenv'


@nox.session(
    venv_backend=env, python=PYTHON_VERSIONS
)  # use this annotation on the wrapper works like a charm
def format(session: nox.Session) -> None:
    """
    format session uising black pylint and flake8
    Parameters
    ----------
    session : nox_session
    """
    session.install(
        "-r", "requirements/format-requirements.txt"
    )  # installe les dependances
    try:
        session.run("black", "--exclude", ".nox", ".")  # formate le code
        session.run("isort", ".")  # formate les imports
    except Exception as e:
        print("formatting failed")
        print(e)


@nox.session(venv_backend=env, python=PYTHON_VERSIONS)
def dev(session: nox.Session) -> None:
    """_summary_

    Args:
        session (nox.Session): _description_
    """
    session.install(
        "-r", "requirements/dev-requirements.txt"
    )


@nox.session(venv_backend=env, python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    session.install("-r", "requirements/test-requirements.txt")
    try:
        session.run("python", "-u", "test/main_test.py")
    except Exception as e:
        print("test failed")
        print(e)
        # check if ll test passed well


@nox.session(venv_backend=env, python=PYTHON_VERSIONS)
def docs(session: nox.Session) -> None:
    session.install("-r", "requirements/docs-requirements.txt")
    session.run("sphinx-build", "-b", "html", "./sphinx/source", "./docs")
    session.run("touch", "docs/.nojekyll")
    session.run("firefox", "docs/index.html")


@nox.session(venv_backend=env, python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    session.install("-r", "requirements/lint-requirements.txt")


@nox.session(venv_backend=env, python=PYTHON_VERSIONS)
def build(session: nox.Session) -> None:
    session.install("-r", "requirements/build-requirements.txt")
