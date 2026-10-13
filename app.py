import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from codeaid.context import collect_context, format_context
from codeaid.runner import DEMO_PROJECT, run_bundled_demo


load_dotenv()

st.set_page_config(page_title="CodeAid", page_icon="🩺", layout="wide")
st.title("CodeAid")
st.caption("Diagnose failing tests, inspect evidence, and verify focused fixes.")

demo_tab, connection_tab = st.tabs(["Offline demo", "Nebius connection"])

with demo_tab:
    st.subheader("Start with a known failure")
    st.write(
        "Run the bundled Python example to see how CodeAid captures test output "
        "and prepares a small, redacted source bundle. This demo does not need a token."
    )
    st.warning(
        "Only the CodeAid-owned demo fixture is executed. Arbitrary repositories "
        "are not run by this prototype."
    )

    if st.button("Run the bundled failing example", type="primary"):
        with st.spinner("Running the demo in a temporary copy…"):
            try:
                st.session_state["demo_result"] = run_bundled_demo()
                st.session_state["demo_context"] = collect_context(DEMO_PROJECT)
                st.session_state.pop("demo_error", None)
            except Exception as exc:
                st.session_state["demo_error"] = type(exc).__name__

    if st.session_state.get("demo_error"):
        st.error(
            "The demo could not run "
            f"({st.session_state['demo_error']}). Install the project requirements "
            "and try again."
        )

    result = st.session_state.get("demo_result")
    if result is not None:
        if result.timed_out:
            st.error(f"The demo exceeded its time limit ({result.duration_seconds:.1f}s).")
        elif result.passed:
            st.info("The demo passed; its intentional bug may have been changed.")
        else:
            st.info(
                "The demo process returned a failure. The fixture is intentionally "
                "broken; check the output below to confirm pytest ran successfully."
            )

        first, second = st.columns(2)
        first.metric("Exit code", result.return_code if result.return_code is not None else "Timed out")
        second.metric("Runtime", f"{result.duration_seconds:.2f}s")
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        st.code(output or "The process returned no output.", language="text")

        bundle = st.session_state.get("demo_context")
        if bundle is not None:
            st.caption(
                f"Prepared {len(bundle.files)} source files ({bundle.total_characters:,} characters); "
                f"skipped {bundle.skipped_files} files. Secrets are filtered before model use."
            )
            with st.expander("Review the source bundle prepared for analysis"):
                st.code(format_context(bundle), language="markdown")

with connection_tab:
    st.subheader("Nebius Token Factory")
    st.write("Once your account is ready, add the key and a model ID to your local `.env` file.")

    if st.button("Check Nebius connection"):
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

    st.caption("The API key is read from `.env` and is never displayed in the app.")
