"""Validate built distributions and smoke-test the wheel in isolation."""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from shutil import which

from aiomonzo import __version__

_PACKAGE_FILES = {
    "aiomonzo/__init__.py",
    "aiomonzo/_version.py",
    "aiomonzo/auth.py",
    "aiomonzo/client.py",
    "aiomonzo/exceptions.py",
    "aiomonzo/models.py",
    "aiomonzo/py.typed",
    "aiomonzo/transport.py",
}
_SDIST_FILES = {
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "docs/API-Reference.md",
    "docs/Development.md",
    "docs/Errors-and-Retries.md",
    "docs/Getting-Started.md",
    "docs/OAuth-Setup.md",
    "docs/README.md",
    "docs/Security.md",
    "docs/Token-Storage.md",
    "docs/Troubleshooting.md",
    "docs/_Footer.md",
    "docs/_Sidebar.md",
}


def _uv_executable() -> str:
    executable = which("uv")
    if executable is None:
        raise RuntimeError("uv is required to validate built distributions")
    return executable


def _single_artifact(dist: Path, pattern: str) -> Path:
    matches = sorted(dist.glob(pattern))
    if len(matches) != 1:
        message = f"Expected one {pattern} artifact, found {len(matches)}"
        raise RuntimeError(message)
    return matches[0]


def _validate_wheel(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        metadata_files = [
            name for name in names if name.endswith(".dist-info/METADATA")
        ]
        license_files = [
            name for name in names if name.endswith(".dist-info/licenses/LICENSE")
        ]
        if len(metadata_files) != 1 or len(license_files) != 1:
            raise RuntimeError("Wheel must contain one metadata and license file")
        metadata = archive.read(metadata_files[0]).decode()
    missing = _PACKAGE_FILES - names
    if missing:
        message = f"Wheel is missing expected files: {sorted(missing)}"
        raise RuntimeError(message)
    if (
        "Name: aiomonzo\n" not in metadata
        or f"Version: {__version__}\n" not in metadata
    ):
        raise RuntimeError("Wheel metadata has an unexpected name or version")


def _validate_sdist(sdist: Path) -> None:
    with tarfile.open(sdist, mode="r:gz") as archive:
        names = archive.getnames()
    roots = {name.split("/", maxsplit=1)[0] for name in names if "/" in name}
    if len(roots) != 1:
        message = f"Expected one sdist root, found {sorted(roots)}"
        raise RuntimeError(message)
    root = roots.pop()
    expected = {
        *(f"{root}/{name}" for name in _SDIST_FILES),
        *(f"{root}/src/{name}" for name in _PACKAGE_FILES),
    }
    missing = expected - set(names)
    if missing:
        message = f"Source distribution is missing files: {sorted(missing)}"
        raise RuntimeError(message)


def _isolated_wheel_smoke(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="aiomonzo-dist-") as temp_dir:
        environment = Path(temp_dir) / ".venv"
        uv = _uv_executable()
        subprocess.run(
            [uv, "venv", "--python", sys.executable, str(environment)],
            check=True,
        )
        executable = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
        python = environment / executable
        subprocess.run(
            [uv, "pip", "install", "--python", str(python), str(wheel)],
            check=True,
        )
        smoke = (
            "import asyncio, pathlib, aiomonzo; "
            f"assert aiomonzo.__version__ == {__version__!r}; "
            "client = aiomonzo.MonzoClient(access_token='offline-test-token'); "
            "asyncio.run(client.aclose()); "
            "assert '.venv' in pathlib.Path(aiomonzo.__file__).parts"
        )
        subprocess.run([str(python), "-I", "-c", smoke], check=True)


def main() -> None:
    """Validate exactly one wheel and sdist in the local dist directory."""
    dist = Path("dist")
    wheel = _single_artifact(dist, "*.whl")
    sdist = _single_artifact(dist, "*.tar.gz")
    _validate_wheel(wheel)
    _validate_sdist(sdist)
    _isolated_wheel_smoke(wheel.resolve())


if __name__ == "__main__":
    main()
