"""get_job tool — retrieve status and results for a transcription job."""

import json
import sys

from salad_transcription_mcp.config import SALAD_ORG_NAME, sdk
from salad_transcription_mcp.utils import serialize_job


def get_job(job_id: str) -> str:
    """Check the status of a transcription job and retrieve results.

    When status is 'succeeded', the output field contains the transcript,
    timestamps, SRT content, translations, summary, and any other requested
    features. Call this after submitting a job with the transcribe tool.

    Possible status values: pending, running, succeeded, failed, cancelled.

    Args:
        job_id: The job ID returned by the transcribe tool.
    """
    try:
        job = sdk.get_transcription_job(
            organization_name=SALAD_ORG_NAME,
            job_id=job_id,
        )
    except Exception as exc:
        print(f"get_job: SDK error: {exc}", file=sys.stderr)
        return json.dumps({"error": str(exc)})

    result = serialize_job(job)
    return json.dumps(result)
