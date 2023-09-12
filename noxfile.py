"""Nox sessions."""
import sys

import nox
from nox_poetry import Session, session

package = "photo_api"
locations = "photo_api", "tests", "noxfile.py"
nox.options.envdir = ".cache"
nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = True
nox.options.sessions = (
    "lint",
    "mypy",
    "safety",
    "tests",
)


@session(python=["3.11"])
def clean(session: Session) -> None:
    """Clean the project."""
    session.install("pyclean")
    session.run("pyclean", ".")
    session.run(
        "rm",
        "-rf",
        ".cache",
        external=True,
    )
    session.run(
        "rm",
        "-rf",
        ".pytest_cache",
        external=True,
    )
    session.run(
        "rm",
        "-rf",
        ".pytype",
        external=True,
    )
    session.run(
        "rm",
        "-rf",
        "dist",
        external=True,
    )
    session.run(
        "rm",
        "-rf",
        ".mypy_cache",
        external=True,
    )
    session.run(
        "rm",
        "-f",
        ".coverage",
        external=True,
    )


@session(python="3.11")
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.install(".")
    session.install(
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "docker",
        "anyio",
        "httpx",
        "pillow",
    )
    session.run(
        "pytest",
        "-ra",
        *args,
    )


@session(python="3.11")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@session(python="3.11")
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
        "flake8-assertive",
    )
    session.run("flake8", *args)


@session(python="3.11")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.poetry.export_requirements()
    session.install("safety")
    session.run("safety", "check", "--full-report", f"--file={requirements}")


@session(python="3.11")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or [
        "--install-types",
        "--non-interactive",
        "photo_api",
        "tests",
    ]
    session.install(".")
    session.install("mypy", "pytest")
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python="3.11")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
