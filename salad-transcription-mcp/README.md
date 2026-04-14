# salad-transcription-mcp

MCP server that wraps the [Salad Transcription API](https://docs.salad.com/reference/transcription), giving LLMs and agents the ability to transcribe audio and video files through tool calls.

## What it does

Exposes two MCP tools:

| Tool         | Description                                                                                                          |
| ------------ | -------------------------------------------------------------------------------------------------------------------- |
| `transcribe` | Submit an audio/video URL for transcription. Returns immediately with a job ID.                                      |
| `get_job`    | Poll for results by job ID. When `status` is `succeeded`, `output` contains the transcript and any requested extras. |

Supported features (all optional): speaker diarization, SRT captions, sentence/word timestamps, translation to English, LLM-powered summarization, multi-language LLM translation, custom vocabulary, custom LLM prompts, text classification, sentiment analysis, multichannel audio.

## Requirements

- Python 3.11+
- A [SaladCloud account](https://portal.salad.com) with an API key
- Your SaladCloud organization name

## Installation

### With uv (recommended)

```bash
uv tool install salad-transcription-mcp
```

Or run directly without installing:

```bash
uvx salad-transcription-mcp
```

### With pip

```bash
pip install salad-transcription-mcp
```

### From source

```bash
git clone https://github.com/saladtechnologies-oss/salad-transcription-mcp
cd salad-transcription-mcp
uv sync
```

## Credentials

The server reads two required environment variables at startup and exits immediately with a clear error if either is missing:

| Variable         | Description                                                                                        |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| `SALAD_API_KEY`  | Your SaladCloud API key. Found in the [SaladCloud portal](https://app.salad.com) under API Access. |
| `SALAD_ORG_NAME` | Your SaladCloud organization name (the slug, e.g. `acme-corp`).                                    |

Never put credentials directly in config files that get committed to version control. Use your MCP client's environment variable support (shown below) instead.

## Connecting to an LLM client

### Claude Desktop / Claude Code

Add to your `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "salad-transcription": {
      "command": "uvx",
      "args": ["salad-transcription-mcp"],
      "env": {
        "SALAD_API_KEY": "your-api-key",
        "SALAD_ORG_NAME": "your-org-name"
      }
    }
  }
}
```

Or if installed with pip:

```json
{
  "mcpServers": {
    "salad-transcription": {
      "command": "python",
      "args": ["-m", "salad_transcription_mcp"],
      "env": {
        "SALAD_API_KEY": "your-api-key",
        "SALAD_ORG_NAME": "your-org-name"
      }
    }
  }
}
```

### Cursor

In `.cursor/mcp.json` at the project root, or `~/.cursor/mcp.json` globally:

```json
{
  "mcpServers": {
    "salad-transcription": {
      "command": "uvx",
      "args": ["salad-transcription-mcp"],
      "env": {
        "SALAD_API_KEY": "your-api-key",
        "SALAD_ORG_NAME": "your-org-name"
      }
    }
  }
}
```

### Continue (VS Code extension)

In `%USERPROFILE%\.continue\config.yaml` (Windows) or `~/.continue/config.yaml` (macOS/Linux):

```yaml
mcpServers:
  - name: Transcription
    command: uvx
    args:
      - salad-transcription-mcp
    env:
      SALAD_API_KEY: "your-api-key"
      SALAD_ORG_NAME: "your-org-name"
```

**Running from WSL on Windows:** VS Code runs in the Windows environment, so `uvx` must be in the Windows PATH. If you're developing in WSL, point directly at the venv Python instead and use `WSLENV` to forward the credentials into WSL:

```yaml
mcpServers:
  - name: Transcription
    command: wsl
    args:
      - /home/<your-user>/projects/salad-transcription-mcp/salad-transcription-mcp/.venv/bin/python
      - -m
      - salad_transcription_mcp
    env:
      SALAD_API_KEY: "your-api-key"
      SALAD_ORG_NAME: "your-org-name"
      WSLENV: "SALAD_API_KEY/u:SALAD_ORG_NAME/u"
```

`WSLENV` tells Windows to forward the listed variables into the WSL process. Without it the server starts but can't read the credentials and exits immediately.

### Any MCP-compatible client (generic stdio config)

```json
{
  "command": "uvx",
  "args": ["salad-transcription-mcp"],
  "env": {
    "SALAD_API_KEY": "your-api-key",
    "SALAD_ORG_NAME": "your-org-name"
  }
}
```

## Testing with MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) lets you test tools interactively before wiring them into an LLM.

```bash
SALAD_API_KEY=your-key SALAD_ORG_NAME=your-org \
  npx @modelcontextprotocol/inspector \
  uvx salad-transcription-mcp
```

Or from source:

```bash
cd salad-transcription-mcp
SALAD_API_KEY=your-key SALAD_ORG_NAME=your-org \
  npx @modelcontextprotocol/inspector \
  uv run python -m salad_transcription_mcp
```

Open the Inspector UI in your browser, select the `transcribe` tool, paste a public audio URL, and submit. Then call `get_job` with the returned ID to poll for results.

## Using with LLMs and agents

Once connected, the LLM handles the tool call loop automatically. A typical interaction:

> **User:** Transcribe this interview and give me a summary: https://example.com/interview.mp3

The model will:
1. Call `transcribe` with the URL and `summarize` set to an appropriate word count.
2. Call `get_job` in a loop until `status` is `succeeded`.
3. Return the transcript and summary from `output`.

### Example prompts

**Basic transcription:**
> Transcribe https://example.com/audio.mp3

**With speaker labels:**
> Transcribe https://example.com/meeting.mp4 with speaker diarization. Language is English.

**Summarize a long recording:**
> Transcribe and summarize this podcast in under 200 words: https://example.com/episode.mp3

**Generate SRT captions:**
> Create SRT captions for https://example.com/video.mp4

**Translate to English:**
> Transcribe this French audio and translate it to English: https://example.com/french.mp3

**Multi-language LLM translation:**
> Transcribe this file and give me translations in French and Spanish: https://example.com/audio.mp3

**Classify content:**
> Transcribe and classify this recording as either Interview, Meeting, or Presentation: https://example.com/call.mp3

**Sentiment analysis:**
> Transcribe this customer call and analyze the sentiment: https://example.com/support.mp3

**Custom prompt:**
> Transcribe this audio and extract all action items mentioned: https://example.com/standup.mp3

### Using with agents / SDKs

If you're building an agent with the Anthropic SDK, configure the server in your MCP server list and the tools appear automatically:

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    mcp_servers=[
        {
            "type": "stdio",
            "command": "uvx",
            "args": ["salad-transcription-mcp"],
            "env": {
                "SALAD_API_KEY": "your-api-key",
                "SALAD_ORG_NAME": "your-org-name",
            },
        }
    ],
    messages=[
        {"role": "user", "content": "Transcribe https://example.com/audio.mp3 and summarize it in 100 words."}
    ],
)
```

Because `transcribe` returns immediately with a job ID, the model needs to poll `get_job` — most capable models handle this correctly from the tool descriptions alone.

## Tool reference

### `transcribe`

Submit a job. All parameters except `url` are optional.

| Parameter                    | Type    | Default  | Description                                                                                                                                          |
| ---------------------------- | ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `url`                        | string  | required | Public URL to audio/video file. Max 2.5h, max 3GB.                                                                                                   |
| `language_code`              | string  | `"en"`   | ISO 639-1 code. Required for diarization.                                                                                                            |
| `return_as_file`             | boolean | `false`  | Return output as a downloadable URL instead of inline JSON.                                                                                          |
| `sentence_level_timestamps`  | boolean | `true`   | Timestamps per sentence.                                                                                                                             |
| `word_level_timestamps`      | boolean | `false`  | Timestamps per word.                                                                                                                                 |
| `diarization`                | boolean | `false`  | Speaker separation.                                                                                                                                  |
| `sentence_diarization`       | boolean | `false`  | Speaker label per sentence.                                                                                                                          |
| `multichannel`               | boolean | `false`  | Transcribe channels separately.                                                                                                                      |
| `srt`                        | boolean | `false`  | Generate SRT captions.                                                                                                                               |
| `translate`                  | string  | —        | `"to_eng"` to translate into English (replaces original).                                                                                            |
| `summarize`                  | integer | `0`      | Max word count for LLM summary. `0` = skip.                                                                                                          |
| `llm_translation`            | string  | —        | Comma-separated languages for LLM translation alongside the original. Supported: English, French, German, Italian, Portuguese, Hindi, Spanish, Thai. |
| `srt_translation`            | string  | —        | Comma-separated languages for SRT translation. Same supported languages.                                                                             |
| `custom_prompt`              | string  | —        | LLM instruction applied to the transcript. Result in `output.llm_result`.                                                                            |
| `custom_vocabulary`          | string  | —        | Comma-separated terms to improve accuracy. Result in `output.llm_custom_vocabulary`.                                                                 |
| `overall_classification`     | boolean | —        | Classify transcript into labels. Requires `classification_labels`.                                                                                   |
| `classification_labels`      | string  | —        | Comma-separated labels, e.g. `"Interview, Meeting, Presentation"`.                                                                                   |
| `overall_sentiment_analysis` | boolean | —        | Sentiment analysis of the full transcript. Result in `output.overall_sentiment`.                                                                     |
| `webhook`                    | string  | —        | URL for job completion callback.                                                                                                                     |
| `metadata`                   | object  | —        | Arbitrary key-value pairs attached to the job.                                                                                                       |

**Returns:** `{ "id": "...", "status": "pending", ... }`

### `get_job`

| Parameter | Type   | Description               |
| --------- | ------ | ------------------------- |
| `job_id`  | string | Job ID from `transcribe`. |

**Returns:** Full job object. When `status` is `"succeeded"`, `output` contains:

| Field                       | Present when                                          |
| --------------------------- | ----------------------------------------------------- |
| `text`                      | Always                                                |
| `sentence_level_timestamps` | `sentence_level_timestamps` or `sentence_diarization` |
| `word_segments`             | `word_level_timestamps` or `diarization`              |
| `srt_content`               | `srt` was set                                         |
| `summary`                   | `summarize` > 0                                       |
| `llm_translation`           | `llm_translation` was set                             |
| `srt_translation`           | `srt_translation` was set                             |
| `llm_custom_vocabulary`     | `custom_vocabulary` was set                           |
| `llm_result`                | `custom_prompt` was set                               |
| `overall_classification`    | `overall_classification` was set                      |
| `overall_sentiment`         | `overall_sentiment_analysis` was set                  |
| `duration_in_seconds`       | Always                                                |
| `processing_time`           | Always                                                |

**Job statuses:** `pending` → `running` → `succeeded` / `failed` / `cancelled`

## Local file upload

The underlying SDK transparently uploads local files to Salad's temporary storage (S4) when you pass a file path as the `url`. Files are stored for 30 days, max 100MB.

```
# This works — the SDK detects it's a local path and uploads first
url: /path/to/audio.mp3
```

## License

MIT
