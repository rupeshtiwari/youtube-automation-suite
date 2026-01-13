import os
import re
import wave
import requests


ELEVENLABS_API_KEY = os.getenv(
    "ELEVENLABS_API_KEY",
    "a3866a55d6767143c99fcf533f780b6ada0a6653268cc1c859c8e9713a92cc64",
)
VOICE_ID = os.getenv(
    "ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB"
)  # default: "Adam" example voice id
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")
OUTPUT_FORMAT = os.getenv(
    "ELEVENLABS_OUTPUT_FORMAT", "pcm_22050"
)  # pcm_16000 / pcm_22050 / pcm_24000 / pcm_44100


def _sample_rate_from_output_format(output_format: str) -> int:
    """
    ElevenLabs output_format examples:
      - mp3_44100_128
      - pcm_22050
      - pcm_44100 (may require higher tier)
    """
    m = re.match(r"^(?:mp3|pcm|ulaw)_(\d+)", output_format)
    if not m:
        raise ValueError(f"Unrecognized output_format: {output_format}")
    return int(m.group(1))


def paragraph_to_wav(paragraph: str, out_wav_path: str) -> str:
    """
    Convert text to speech using Eleven Labs API and save as WAV file.

    Args:
        paragraph: Text to convert to speech
        out_wav_path: Path where the WAV file should be saved

    Returns:
        Path to the created WAV file

    Raises:
        RuntimeError: If ELEVENLABS_API_KEY is not set
        requests.HTTPError: If API request fails
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError(
            "Missing ELEVENLABS_API_KEY env var. "
            "Please set it: export ELEVENLABS_API_KEY='your-api-key'"
        )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    params = {"output_format": OUTPUT_FORMAT}  # request raw PCM so we can write WAV
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg, audio/wav, audio/*;q=0.9, */*;q=0.8",
    }
    payload = {
        "text": paragraph,
        "model_id": MODEL_ID,
        # Optional: voice_settings, pronunciation dictionaries, etc.
        # "voice_settings": {"stability": 0.3, "similarity_boost": 0.8, "style": 0.0, "use_speaker_boost": True},
    }

    # Stream the audio bytes
    with requests.post(
        url, params=params, headers=headers, json=payload, stream=True, timeout=120
    ) as r:
        r.raise_for_status()

        sample_rate = _sample_rate_from_output_format(OUTPUT_FORMAT)
        channels = 1  # ElevenLabs TTS is typically mono for PCM
        sampwidth = 2  # PCM S16LE = 16-bit = 2 bytes

        # Write WAV container around raw PCM
        with wave.open(out_wav_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)

            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
                    wf.writeframes(chunk)

    return out_wav_path


if __name__ == "__main__":
    text = (
        "Here’s a short paragraph you want to convert to speech. "
        "It can be multiple sentences, and it will come out as a WAV file."
    )
    path = paragraph_to_wav(text, "output.wav")
    print("Saved:", path)
