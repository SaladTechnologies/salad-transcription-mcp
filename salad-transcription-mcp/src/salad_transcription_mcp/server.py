"""MCP server entry point.

Registers the transcribe and get_job tools and starts the server
on stdio transport (the MCP convention for CLI-launched servers).
"""

from mcp.server.fastmcp import FastMCP

from salad_transcription_mcp.tools.get_job import get_job
from salad_transcription_mcp.tools.transcribe import transcribe

mcp = FastMCP(
    "salad-transcription",
    instructions=(
        "This server provides tools for transcribing audio and video files "
        "using the Salad Transcription API. "
        "Use 'transcribe' to submit a job and 'get_job' to poll for results."
    ),
)

mcp.tool()(transcribe)
mcp.tool()(get_job)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
