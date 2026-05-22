"""
AI image generation for the daily financial digest.
Generates a market sentiment banner image via Muapi.ai.
Returns a hosted URL to embed directly in the email HTML.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from opengenai_client import OpenGenAIClient


SENTIMENT_PROMPTS = {
    "bullish": (
        "Financial market bull, golden hour lighting, green rising chart lines in background, "
        "cinematic 16:9, photorealistic, dramatic upward momentum, Wall Street aesthetic, "
        "deep blue and emerald green palette, high contrast, Bloomberg terminal vibes"
    ),
    "bearish": (
        "Financial market bear, stormy dramatic sky, red falling chart lines in background, "
        "cinematic 16:9, photorealistic, dark moody atmosphere, Wall Street aesthetic, "
        "deep crimson and charcoal palette, high contrast, Bloomberg terminal vibes"
    ),
    "neutral": (
        "Financial market scales balanced, neutral grey tones, sideways chart lines in background, "
        "cinematic 16:9, photorealistic, calm professional atmosphere, Wall Street aesthetic, "
        "silver and slate blue palette, high contrast, Bloomberg terminal vibes"
    ),
}


def generate_digest_banner(sentiment: str, date: str, save_local: bool = True) -> str | None:
    """
    Generate a market sentiment banner image.

    Args:
        sentiment: 'bullish', 'bearish', or 'neutral'
        date:      e.g. '2026-05-20'
        save_local: also save to output/images/

    Returns:
        Hosted image URL (for embedding in email), or None if MUAPI_API_KEY not set.
    """
    api_key = os.getenv("MUAPI_API_KEY")
    if not api_key:
        return None

    sentiment = sentiment.lower()
    prompt = SENTIMENT_PROMPTS.get(sentiment, SENTIMENT_PROMPTS["neutral"])
    prompt += f", digital art, financial news header for {date}"

    try:
        client = OpenGenAIClient(api_key)
        print(f"  [Image] Generating {sentiment} banner for {date}...")
        image_url = client.text_to_image(prompt)
        print(f"  [Image] Banner ready: {image_url}")

        if save_local:
            local_path = Path("output/images") / f"banner_{date}_{sentiment}.png"
            client.download(image_url, str(local_path))
            print(f"  [Image] Saved locally: {local_path}")

        return image_url
    except Exception as e:
        print(f"  [Image] Generation failed (non-fatal): {e}")
        return None


def inject_banner_into_html(html: str, image_url: str) -> str:
    """Insert an <img> banner right after the .header div in the email HTML."""
    banner_html = (
        f'<div style="width:100%;overflow:hidden;max-height:200px;">'
        f'<img src="{image_url}" alt="market sentiment" '
        f'style="width:100%;height:200px;object-fit:cover;display:block;" />'
        f'</div>'
    )
    return re.sub(
        r'(</div>\s*)(.*?)(class="tldr")',
        lambda m: m.group(1) + banner_html + m.group(2) + m.group(3),
        html,
        count=1,
        flags=re.DOTALL,
    )
