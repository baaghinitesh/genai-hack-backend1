import os
from google import genai


def main():
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        raise SystemExit("GOOGLE_API_KEY not set")

    # Gemini 2.5 Flash example prompt
    prompt = "Explain in one sentence how to practice mindful breathing."

    client = genai.Client(api_key=api_key)
    result = client.models.generate(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    # The SDK returns a rich object; extract text parts
    text = "".join([p.text for c in result.candidates for p in c.content.parts if hasattr(p, "text")])
    print(text or result)


if __name__ == "__main__":
    main()


