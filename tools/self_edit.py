from pathlib import Path

BASE_DIR = Path("tools").resolve()


def _safe(path: str) -> Path:
    p = (BASE_DIR / path).resolve()
    if not str(p).startswith(str(BASE_DIR)):
        raise ValueError("Access outside tools/ is not allowed")
    return p


def register(server):

    @server.tool()
    def self_edit(
        action: str,
        file_path: str,
        content: str = ""
    ) -> str:
        """
        Actions: create, read, write, delete
        """
        path = _safe(file_path)

        if action == "create":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return f"Created {file_path}"

        if action == "read":
            return path.read_text() if path.exists() else "File not found"

        if action == "write":
            if not path.exists():
                return "File not found"
            path.write_text(content)
            return f"Updated {file_path}"

        if action == "delete":
            if path.exists():
                path.unlink()
                return f"Deleted {file_path}"
            return "File not found"

        raise ValueError("Invalid action")
