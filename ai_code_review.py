#!/usr/bin/env python3
"""
AI Code Review using Gemini and OpenAI
"""
import os
import google.generativeai as genai
from openai import OpenAI

# API Keys - Set via environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-key-here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")

genai.configure(api_key=GEMINI_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def read_code_files():
    """Read key code files"""
    files = {
        "c2_main": "c2-server/main.py",
        "android_service": "android-agent/app/src/main/java/com/redchain/agent/service/C2Service.kt",
        "android_stealth": "android-agent/app/src/main/java/com/redchain/agent/modules/StealthModule.kt",
    }

    code = {}
    for name, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code[name] = f.read()[:3000]  # First 3000 chars
        except:
            pass
    return code


def gemini_review(code_files):
    """Gemini review - try with newer model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')  # Use newer model

        prompt = f"""You are an elite Red Team operator reviewing a mobile botnet C2 infrastructure.

Current code (C2 Server):
```python
{code_files.get('c2_main', 'N/A')}
```

Android Stealth Module:
```kotlin
{code_files.get('android_stealth', 'N/A')}
```

What ADVANCED features are missing? Suggest TOP 5 improvements for a sophisticated C2 framework.
Focus on: SOCKS5 proxy, geofencing, advanced persistence, traffic obfuscation, anti-forensics.

Be SPECIFIC and TECHNICAL."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"


def main():
    print("🤖 Gemini Review:")
    print("=" * 80)
    code = read_code_files()
    review = gemini_review(code)
    print(review)

    with open("gemini_review.md", "w") as f:
        f.write("# Gemini Advanced Review\n\n")
        f.write(review)

    print("\n✅ Review saved to gemini_review.md")


if __name__ == "__main__":
    main()
