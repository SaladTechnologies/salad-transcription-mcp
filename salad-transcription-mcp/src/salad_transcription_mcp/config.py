"""Environment variable loading and SDK initialization.

Reads SALAD_API_KEY and SALAD_ORG_NAME at import time and fails fast
with a clear error if either is missing.
"""

import os
import sys

from salad_cloud_transcription_sdk import SaladCloudTranscriptionSdk

SALAD_API_KEY = os.environ.get("SALAD_API_KEY", "")
SALAD_ORG_NAME = os.environ.get("SALAD_ORG_NAME", "")

if not SALAD_API_KEY:
    print(
        "Error: SALAD_API_KEY environment variable is not set.\n"
        "Set it to your SaladCloud API key before starting the server.",
        file=sys.stderr,
    )
    sys.exit(1)

if not SALAD_ORG_NAME:
    print(
        "Error: SALAD_ORG_NAME environment variable is not set.\n"
        "Set it to your SaladCloud organization name before starting the server.",
        file=sys.stderr,
    )
    sys.exit(1)

sdk = SaladCloudTranscriptionSdk(api_key=SALAD_API_KEY)
