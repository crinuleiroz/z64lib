from pathlib import Path

def open_read(path: Path | str, **kwargs):
    """
    Open a file and return its contents.

    Parameters
    ----------
    path: str | Path
        Path to the file.
    **kwargs: dict
        Additional arguments to pass to open(), like mode='r', encoding='utf-8',
        buffering=1, etc.

    Returns
    ----------
    bytes | str
        Contents of the file, depending on mode.
    """
    with open(path, **kwargs) as f:
        return f.read()