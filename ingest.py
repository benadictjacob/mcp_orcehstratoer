from pathlib import Path

TOOLS_DIR = Path("tools")


def ingest_repo_as_tool(repo_name: str) -> str:
    tool_file = TOOLS_DIR / f"{repo_name}.py"

    tool_file.write_text(
        f'''
def register(server):

    @server.tool()
    def {repo_name}_hello(name: str = "world") -> str:
        return "Hello " + name
'''
    )

    return f"Repo '{repo_name}' ingested as tool."
