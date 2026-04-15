"""transcribe_lite tool — submit a job to the Transcription Lite endpoint.

The Lite endpoint has a minimal input schema: it only accepts `url` in the
input object and rejects any extra fields (returning 400).  We bypass
TranscriptionJobInput entirely and construct the payload dict directly, then
call the underlying SaladCloudSdk inference endpoint directly.
"""

import json
import sys
from typing import Optional

from salad_cloud_sdk.models import InferenceEndpointJobPrototype
from salad_cloud_transcription_sdk.net.environment.environment import (
    LITE_TRANSCRIPTION_ENDPOINT_NAME,
)

from salad_transcription_mcp.config import SALAD_ORG_NAME, sdk
from salad_transcription_mcp.utils import serialize_job


def transcribe_lite(
    url: str,
    webhook: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> str:
    """Submit an audio/video file for transcription using the Lite engine.

    Faster and cheaper than the full transcribe tool (~8x faster, $0.03/hr vs
    $0.16/hr). Returns immediately with a job ID. Use get_job to poll for
    results.

    Lite does not support LLM-powered features (summarization, multi-language
    translation, custom prompts, classification, sentiment analysis) or
    fine-grained options like diarization or SRT. Use the transcribe tool for
    those. Lite is best for bulk or latency-sensitive workloads where just the
    transcript text is needed.

    Args:
        url: Publicly accessible URL to audio/video file. Direct download link.
            Max 2.5 hours, max 3GB. Supports MP4, MOV, WAV, MP3, FLAC, etc.
        webhook: URL to receive a POST callback when the job completes.
        metadata: Arbitrary key-value pairs to attach to the job.
    """
    service = sdk.transcription

    try:
        # Resolve URL (uploads to S4 if a local path is given)
        file_url = service._process_source(url, SALAD_ORG_NAME)

        input_dict: dict = {"url": file_url}

        prototype_kwargs: dict = {"input": input_dict}
        if webhook is not None:
            prototype_kwargs["webhook"] = webhook
            prototype_kwargs["webhook_url"] = webhook
        if metadata is not None:
            prototype_kwargs["metadata"] = metadata

        job = service._salad_sdk.inference_endpoints.create_inference_endpoint_job(
            request_body=InferenceEndpointJobPrototype(**prototype_kwargs),
            organization_name=SALAD_ORG_NAME,
            inference_endpoint_name=LITE_TRANSCRIPTION_ENDPOINT_NAME,
        )
        service._convert_job_output(job)
    except Exception as exc:
        print(f"transcribe_lite: error: {exc}", file=sys.stderr)
        return json.dumps({"error": str(exc)})

    return json.dumps(serialize_job(job))
