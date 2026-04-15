"""get_job tool — retrieve status and results for a transcription job."""

import json
import sys
from typing import Literal, Optional

from salad_cloud_transcription_sdk.net.environment.environment import (
    FULL_TRANSCRIPTION_ENDPOINT_NAME,
    LITE_TRANSCRIPTION_ENDPOINT_NAME,
)

from salad_transcription_mcp.config import SALAD_ORG_NAME, sdk
from salad_transcription_mcp.utils import serialize_job


def get_job(job_id: str, engine: Optional[Literal["full", "lite"]] = "full") -> str:
    """Check the status of a transcription job and retrieve results.

    When status is 'succeeded', the output field contains the transcript,
    timestamps, SRT content, translations, summary, and any other requested
    features. Call this after submitting a job with the transcribe or
    transcribe_lite tool.

    Possible status values: pending, running, succeeded, failed, cancelled.

    Args:
        job_id: The job ID returned by transcribe or transcribe_lite.
        engine: Which engine the job was submitted with. Use "lite" for jobs
            created by transcribe_lite, "full" (default) for transcribe.
    """
    endpoint_name = (
        LITE_TRANSCRIPTION_ENDPOINT_NAME if engine == "lite"
        else FULL_TRANSCRIPTION_ENDPOINT_NAME
    )
    service = sdk.transcription
    try:
        job = service._salad_sdk.inference_endpoints.get_inference_endpoint_job(
            organization_name=SALAD_ORG_NAME,
            inference_endpoint_name=endpoint_name,
            inference_endpoint_job_id=job_id,
        )
        service._convert_job_output(job)
    except Exception as exc:
        print(f"get_job: SDK error: {exc}", file=sys.stderr)
        return json.dumps({"error": str(exc)})

    result = serialize_job(job)
    return json.dumps(result)
