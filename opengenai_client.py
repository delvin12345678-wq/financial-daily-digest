"""
Muapi.ai / Open Generative AI REST client.

Auth:    x-api-key header (get key from muapi.ai/access-keys)
Submit:  POST  https://api.muapi.ai/api/v1/{endpoint}
Poll:    GET   https://api.muapi.ai/api/v1/predictions/{id}/result
Upload:  POST  https://api.muapi.ai/api/v1/upload_file
Result:  response["outputs"][0]  — hosted CDN URL

Confirmed model endpoints (May 2026):
  Image  : flux-schnell-image, flux-dev-image, hidream_i1_full_image
  T2V    : seedance-v2.0-t2v (default), kling-v2.6-pro-t2v, wan2.5-text-to-video, veo3.1-text-to-video
  I2V    : seedance-v2.0-i2v (default), kling-v2.6-pro-i2v, wan2.5-image-to-video, veo3.1-image-to-video
  Note: seedance-* I2V uses payload key `images_list` (array) + quality + remove_watermark.
        seedance quality must be 'high' or 'basic' (NOT a resolution like '1080p').
"""

import os
import time
import requests
from pathlib import Path

MUAPI_BASE = "https://api.muapi.ai/api/v1"
POLL_INTERVAL = 5   # seconds (API docs say 3-5s)
MAX_WAIT     = 600  # seconds


class OpenGenAIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MUAPI_API_KEY")
        if not self.api_key:
            raise ValueError("Set MUAPI_API_KEY env var or pass api_key=")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    # ── Image ──────────────────────────────────────────────────────────
    def text_to_image(self, prompt: str, model: str = None, **kwargs) -> str:
        """Returns hosted image URL."""
        model = model or os.getenv("MUAPI_IMAGE_MODEL", "flux-schnell-image")
        return self._submit(model, {"prompt": prompt, **kwargs})

    # ── Video ──────────────────────────────────────────────────────────
    def text_to_video(self, prompt: str, model: str = None, duration: int = 5,
                      aspect_ratio: str = "9:16", **kwargs) -> str:
        """Returns hosted video URL."""
        model = model or os.getenv("MUAPI_VIDEO_MODEL", "seedance-v2.0-t2v")
        payload = {"prompt": prompt, "duration": duration,
                   "aspect_ratio": aspect_ratio, **kwargs}
        if "seedance" in model:
            # Seedance quality must be 'high' or 'basic' (not a resolution string)
            payload.setdefault("quality", "high")
            payload.setdefault("remove_watermark", True)
        return self._submit(model, payload)

    def image_to_video(self, image_url: str, prompt: str = "", model: str = None,
                       duration: int = 5, aspect_ratio: str = "9:16", **kwargs) -> str:
        """Animate a reference image. Returns hosted video URL."""
        model = model or os.getenv("MUAPI_I2V_MODEL", "seedance-v2.0-i2v")
        if "seedance" in model:
            # Seedance I2V expects images_list[] (not image_url) + quality flags.
            # quality must be 'high' or 'basic' (not a resolution string).
            payload = {"prompt": prompt, "images_list": [image_url],
                       "duration": duration, "aspect_ratio": aspect_ratio,
                       "quality": kwargs.pop("quality", "high"),
                       "remove_watermark": kwargs.pop("remove_watermark", True),
                       **kwargs}
        else:
            payload = {"image_url": image_url, "prompt": prompt,
                       "duration": duration, "aspect_ratio": aspect_ratio, **kwargs}
        return self._submit(model, payload)

    # ── File Hosting ───────────────────────────────────────────────────
    def upload_file(self, file_path: str) -> str:
        """Upload local file to Muapi CDN. Returns hosted URL."""
        headers = {"x-api-key": self.api_key}  # no Content-Type; multipart
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{MUAPI_BASE}/upload_file",
                headers=headers,
                files={"file": f},
                timeout=120,
            )
        resp.raise_for_status()
        body = resp.json()
        # upload_file returns {"url": ...}; other endpoints {"outputs": [...]}
        if "url" in body:
            return body["url"]
        return body["outputs"][0]

    def download(self, url: str, output_path: str):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)

    # ── Internal ───────────────────────────────────────────────────────
    def _submit(self, endpoint: str, payload: dict) -> str:
        resp = requests.post(
            f"{MUAPI_BASE}/{endpoint}",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        request_id = body.get("request_id")
        if not request_id:
            raise RuntimeError(f"No request_id in response: {body}")
        print(f"  [Muapi] {endpoint} → job {request_id}")
        return self._poll(request_id)

    def _poll(self, request_id: str) -> str:
        start = time.time()
        while time.time() - start < MAX_WAIT:
            resp = requests.get(
                f"{MUAPI_BASE}/predictions/{request_id}/result",
                headers=self.headers,
                timeout=45,
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "processing")

            if status == "completed":
                outputs = data.get("outputs", [])
                if not outputs:
                    raise RuntimeError(f"No outputs in completed job: {data}")
                return outputs[0]

            if status in ("failed", "cancelled"):
                raise RuntimeError(f"Job {status}: {data.get('error', 'unknown')}")

            elapsed = int(time.time() - start)
            print(f"  [Muapi] {elapsed}s — {status}...")
            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"Job timed out after {MAX_WAIT}s")
