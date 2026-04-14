"""transcribe tool — submit a transcription job and return immediately."""

import json
import sys
from typing import Any, Dict, List, Optional

from salad_cloud_transcription_sdk.models.transcription_engine import TranscriptionEngine
from salad_cloud_transcription_sdk.models.transcription_job_input import (
    TranscriptionJobInput,
    TranslationLanguage,
)
from salad_cloud_transcription_sdk.models.transcription_request import TranscriptionRequest

from salad_transcription_mcp.config import SALAD_ORG_NAME, sdk
from salad_transcription_mcp.utils import serialize_job


class _ExtendedJobInput(TranscriptionJobInput):
    """TranscriptionJobInput extended with fields the SDK model omits.

    The SDK's to_dict() is the serialization path used when building the job
    request (see TranscriptionService.transcribe, line:
        request_dict = request.to_dict()["input"]
    ).  We subclass and override to_dict() so the extra fields are included in
    the payload without forking the SDK.
    """

    def __init__(
        self,
        *args,
        overall_classification: Optional[bool] = None,
        classification_labels: Optional[str] = None,
        overall_sentiment_analysis: Optional[bool] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._overall_classification = overall_classification
        self._classification_labels = classification_labels
        self._overall_sentiment_analysis = overall_sentiment_analysis

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        if self._overall_classification is not None:
            result["overall_classification"] = self._overall_classification
        if self._classification_labels is not None:
            result["classification_labels"] = self._classification_labels
        if self._overall_sentiment_analysis is not None:
            result["overall_sentiment_analysis"] = self._overall_sentiment_analysis
        return result


def _parse_language_list(value: Optional[str]) -> Optional[List[str]]:
    """Split a comma-separated language string into a list."""
    if value is None:
        return None
    return [lang.strip() for lang in value.split(",") if lang.strip()]


def transcribe(
    url: str,
    language_code: str = "en",
    return_as_file: bool = False,
    sentence_level_timestamps: bool = True,
    word_level_timestamps: bool = False,
    diarization: bool = False,
    sentence_diarization: bool = False,
    multichannel: bool = False,
    srt: bool = False,
    translate: Optional[str] = None,
    summarize: int = 0,
    llm_translation: Optional[str] = None,
    srt_translation: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    custom_vocabulary: Optional[str] = None,
    overall_classification: Optional[bool] = None,
    classification_labels: Optional[str] = None,
    overall_sentiment_analysis: Optional[bool] = None,
    webhook: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> str:
    """Submit an audio/video file for transcription.

    Returns immediately with a job ID. Use get_job to poll for results.
    Supports diarization (speaker identification), SRT captions, translation,
    summarization, classification, sentiment analysis, and custom LLM prompts.

    Args:
        url: Publicly accessible URL to audio/video file. Direct download link.
            Max 2.5 hours, max 3GB. Supports MP4, MOV, WAV, MP3, FLAC, etc.
        language_code: ISO 639-1 code (e.g. "en", "fr", "de"). Defaults to
            "en". Required when diarization is enabled.
        return_as_file: When true, output is a downloadable file URL instead of
            inline JSON. Useful for very large transcripts. Default false.
        sentence_level_timestamps: Include timestamps at sentence level.
            Default true.
        word_level_timestamps: Include timestamps at word level. Default false.
        diarization: Speaker separation. Requires language_code. Supported in
            27+ languages. Default false.
        sentence_diarization: Speaker info per sentence (most prominent speaker
            per sentence). Requires language_code. Default false.
        multichannel: Transcribe audio channels separately. Falls back to
            regular diarization if only one channel. Default false.
        srt: Generate SRT subtitle output. Default false.
        translate: Set to "to_eng" to translate transcription into English
            (replaces original transcript).
        summarize: Word limit for LLM-powered summary. Set to 0 (default) to
            skip.
        llm_translation: Comma-separated target languages for LLM translation
            alongside the original. Supported: English, French, German,
            Italian, Portuguese, Hindi, Spanish, Thai.
        srt_translation: Comma-separated target languages for SRT subtitle
            translation. Same supported languages as llm_translation.
        custom_prompt: Freeform LLM instruction applied to the transcript.
            Sent as "{custom_prompt}:{transcription}". Result is in
            output.llm_result.
        custom_vocabulary: Comma-separated domain-specific terms to improve
            recognition accuracy. Result is in output.llm_custom_vocabulary.
        overall_classification: Classify entire transcript into labels. Requires
            classification_labels. Result is in output.overall_classification.
        classification_labels: Comma-separated labels for classification
            (e.g. "Interview, Meeting, Presentation").
        overall_sentiment_analysis: LLM-powered sentiment analysis of the full
            transcript. Result is in output.overall_sentiment. Default false.
        webhook: URL to receive a POST callback when the job completes.
        metadata: Arbitrary key-value pairs to attach to the job.
    """
    input_kwargs: dict[str, Any] = {
        "return_as_file": return_as_file,
        "language_code": language_code,
        "sentence_level_timestamps": sentence_level_timestamps,
        "word_level_timestamps": word_level_timestamps,
        "diarization": diarization,
        "sentence_diarization": sentence_diarization,
        "multichannel": multichannel,
        "srt": srt,
        "summarize": summarize,
    }

    if translate is not None:
        input_kwargs["translate"] = translate
    if custom_prompt is not None:
        input_kwargs["custom_prompt"] = custom_prompt
    if custom_vocabulary is not None:
        input_kwargs["custom_vocabulary"] = custom_vocabulary

    parsed_llm = _parse_language_list(llm_translation)
    if parsed_llm is not None:
        input_kwargs["llm_translation"] = parsed_llm

    parsed_srt = _parse_language_list(srt_translation)
    if parsed_srt is not None:
        input_kwargs["srt_translation"] = parsed_srt

    job_input = _ExtendedJobInput(
        **input_kwargs,
        overall_classification=overall_classification,
        classification_labels=classification_labels,
        overall_sentiment_analysis=overall_sentiment_analysis,
    )

    request = TranscriptionRequest(
        options=job_input,
        webhook=webhook,
        metadata=metadata,
    )

    try:
        job = sdk.transcribe(
            source=url,
            organization_name=SALAD_ORG_NAME,
            request=request,
            engine=TranscriptionEngine.Full,
            auto_poll=False,
        )
    except Exception as exc:
        print(f"transcribe: SDK error: {exc}", file=sys.stderr)
        return json.dumps({"error": str(exc)})

    return json.dumps(serialize_job(job))
