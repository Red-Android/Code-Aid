# CodeAid

CodeAid is a coding assistant that collects evidence from failing tests, explains likely causes, proposes a focused patch, and checks the patch by rerunning tests.

This starter is the first milestone: a small Streamlit app that checks a connection to a Nemotron model through Nebius Token Factory. Model inference is hosted by Nebius, so local GPU compute is not needed for this step.

## Requirements

- Python 3.11 or newer
- Git
- A Nebius Token Factory API key
- Access to a Nemotron model in Token Factory

## Run locally on Linux

From this project directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `NEBIUS_API_KEY` and `NEBIUS_MODEL`. Keep `.env` private; it is excluded from Git. Then launch the app:

```bash
streamlit run app.py
```

Select **Check Nebius connection**. A successful response confirms that the local app can reach the configured model.

## Configuration

| Variable | Purpose |
| --- | --- |
| `NEBIUS_API_KEY` | Token Factory API key |
| `NEBIUS_BASE_URL` | Token Factory OpenAI-compatible API URL |
| `NEBIUS_MODEL` | Exact model ID available to your account |

The current model ID can be found in the Token Factory model catalog. The app does not assume an account-specific model name.

## Safety note

This starter only sends a short connection-check prompt. It does not read or execute a source repository yet. Repository scanning and test execution will be added as separate, bounded steps.
