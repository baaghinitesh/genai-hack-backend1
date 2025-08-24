import os
import sys

from langchain_google_vertexai import ChatVertexAI


def main() -> None:
    

    kwargs = {"model_name": "gemini-2.5-flash", "project": "n8n-local-463912"}
    

    model = ChatVertexAI(**kwargs)
    resp = model.invoke("Reply exactly: Gemini reachable.")
    print(getattr(resp, "content", resp))


if __name__ == "__main__":
    main()


