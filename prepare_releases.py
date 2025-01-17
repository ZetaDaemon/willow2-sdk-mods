import itertools
from pathlib import Path
import tomllib
from argparse import ArgumentParser, ArgumentTypeError
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


def dir_path_arg(arg: str) -> Path:
    """
    Argparse type converter which ensures the arg is a valid directory.

    Args:
        arg: The arg to try parse.
    Returns:
        The corresponding path.
    """
    path = Path(arg)
    if not path.is_dir():
        raise ArgumentTypeError(f"'{path}' is not a valid directory")
    return path.resolve()


if __name__ == "__main__":
    parser = ArgumentParser(description="Prepare the release zips.")
    parser.add_argument(
        "folders",
        nargs="*",
        type=dir_path_arg,
        help="The mod folders to zip. Leave empty to try all.",
    )
    args = parser.parse_args()
    for mod_folder in args.folders or (
        x for x in Path(__file__).parent.iterdir() if x.is_dir()
    ):
        if mod_folder is not Path:
            mod_folder = Path(mod_folder)
        if mod_folder.name.startswith("."):
            continue
        if not (mod_folder / "pyproject.toml").exists():
            continue

        data: dict[str, dict[str, Any]] = tomllib.load(
            (mod_folder / "pyproject.toml").open("rb")
        )
        print(data)
        sdkmod_release_script: dict = data.get("tool", {}).get(
            "sdkmod_release_script", {}
        )
        print(sdkmod_release_script)
        as_zip = sdkmod_release_script.get("as_zip", False)
        file_types = sdkmod_release_script.get("files", [])

        output_file = mod_folder.with_suffix(".zip" if as_zip else ".sdkmod")
        print([file for file in mod_folder.iterdir()])
        print(file_types)

        with ZipFile(output_file, "w", ZIP_DEFLATED, compresslevel=9) as zip_file:
            for file in itertools.chain.from_iterable(
                mod_folder.glob(pattern) for pattern in file_types
            ):
                print("adding", file)
                zip_file.write(file, mod_folder.name / file.relative_to(mod_folder))

            zip_file.write(
                mod_folder / "pyproject.toml",
                mod_folder.name
                / (mod_folder / "pyproject.toml").relative_to(mod_folder),
            )
