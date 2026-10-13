# CodeAid

CodeAid is an AI coding assistant for diagnosing failing Python tests. It gathers a small evidence bundle, asks NVIDIA Nemotron to explain likely causes, proposes a focused patch, and checks a candidate fix by rerunning tests.

## Current prototype

The app includes an offline demo with a deliberately broken discount calculator. It runs that CodeAid-owned fixture in a temporary copy, captures bounded test output, and prepares a redacted source bundle. This part works without a Nebius API key.

The Nemotron connection tab is ready for a Token Factory key and model ID. The model call that diagnoses failures and the patch verification workflow are the next implementation milestones.

## Run locally on Linux

Use Python 3.11 or newer. From the repository directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Open the **Offline demo** tab and select **Run the bundled failing example**. The failure is intentional. No model key is needed for this flow.

To check Nebius access, set these values in your local `.env` file:

```dotenv
NEBIUS_API_KEY=your_key_here
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
NEBIUS_MODEL=your_available_model_id
```

Keep `.env` private; it is excluded from Git. Find the exact model ID in the Token Factory model catalog for your account.

## Safety boundary

- The prototype executes only its bundled demo fixture, never a user-selected repository.
- The demo runs from a temporary copy, with a timeout and a reduced environment that omits the user's API keys.
- Repository context collection skips environment files, likely credential files, generated directories, oversized files, and binary content.
- Common credential patterns are redacted before source or test output is prepared for model use.
- The temporary directory and reduced environment are not a full operating-system sandbox. Broader repository execution needs stronger isolation before it is enabled.

## Project layout

```text
app.py                         Streamlit interface
codeaid/context.py             Bounded source collection and secret redaction
codeaid/runner.py              Bundled-demo test runner
fixtures/broken_python/        Intentional failing example
```

## Hackathon direction

CodeAid targets the Coding and Agentic Engineering track. Its focus is evidence-backed debugging: show the failing test, identify relevant source, explain a likely cause, propose a small diff, and report whether verification passed.
