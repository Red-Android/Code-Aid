import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

st.set_page_config(page_title="CodeAid", page_icon="🩺")
st.title("CodeAid")
st.caption("An assistant for diagnosing failing tests and verifying focused fixes.")

st.info(
    "First milestone: confirm that this app can reach your configured Nemotron "
    "model through Nebius Token Factory."
)

if st.button("Check Nebius connection", type="primary"):
    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    model = os.getenv("NEBIUS_MODEL", "").strip()
    base_url = os.getenv(
        "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"
    ).strip()

    if not api_key:
        st.error("NEBIUS_API_KEY is missing. Add it to your local .env file.")
    elif not model:
        st.error("NEBIUS_MODEL is missing. Set it to a model available to your account.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply with exactly: CodeAid is connected.",
                    }
                ],
            )
            answer = response.choices[0].message.content
            st.success("Nebius request completed.")
            st.write(answer or "The model returned an empty response.")
        except Exception as exc:
            st.error(
                f"The request failed ({type(exc).__name__}). Check your API key, "
                "base URL, model ID, and Token Factory access."
            )

st.caption("Your API key is read from .env and is never displayed in the app.")
