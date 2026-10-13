# CodeAid — Project Requirements

Project folder: `/home/animesh/Documents/GitHub/Code-Aid`

CodeAid is an evidence-first coding assistant that diagnoses failing tests, proposes a focused patch, and verifies the patch by running the tests again.

## 1. Required local software

- [ ] Git
- [ ] Python 3.11 or newer
- [ ] Python virtual environment support (`venv`)
- [ ] A code editor
- [ ] `pytest` for the first supported project type
- [ ] `ruff` for Python linting and formatting
- [ ] `streamlit` for the first demo interface
- [ ] OpenAI Python SDK for the Nebius-compatible API
- [ ] `python-dotenv` for local environment variables

## 2. Required Nebius services

- [ ] Nebius account with Token Factory access
- [ ] Nebius Token Factory API key
- [ ] One Nemotron model available in the account
- [ ] A small test request to confirm the API key and model work
- [ ] A spending or usage limit, if available in the Nebius project settings

Suggested model roles:

- [ ] Nemotron Nano for fast file and test-failure analysis
- [ ] Nemotron Super for difficult multi-file diagnoses and final patch plans

## 3. Required project components

- [ ] Repository loader
- [ ] File and directory ignore rules
- [ ] Project-type detector
- [ ] Safe test-command detector
- [ ] Test runner with timeout handling
- [ ] Structured failure record containing:
  - [ ] Exit code
  - [ ] Standard output and error output
  - [ ] Stack trace
  - [ ] Test name
  - [ ] Relevant source files
  - [ ] Runtime and timestamp
- [ ] Secret and credential redaction
- [ ] Nemotron client wrapper
- [ ] Structured diagnosis schema
- [ ] Patch-generation step
- [ ] Temporary workspace for candidate patches
- [ ] Verification step that reruns targeted tests
- [ ] Human-readable diff viewer
- [ ] Streamlit interface for the demo

## 4. Safety requirements

- [ ] Never allow the model to execute arbitrary shell commands directly
- [ ] Start with an allowlist for safe commands such as `pytest` and read-only inspection
- [ ] Run tests in a disposable temporary workspace
- [ ] Enforce execution timeouts
- [ ] Ignore `.env`, private keys, credentials, `.git`, dependency folders, and large binaries
- [ ] Redact secrets from logs before sending context to Nemotron
- [ ] Do not automatically push commits or delete files
- [ ] Keep network access disabled for test execution unless explicitly required

## 5. Repository and documentation

- [ ] Public GitHub repository
- [ ] Open-source license, preferably MIT or Apache-2.0
- [ ] README with setup and run instructions
- [ ] `.env.example` containing variable names only
- [ ] `.gitignore` excluding secrets, virtual environments, caches, and run artifacts
- [ ] Architecture diagram or simple architecture section
- [ ] Explanation of where Nemotron and Token Factory are used
- [ ] Security and limitations section
- [ ] Reproducible demo instructions

## 6. Evaluation assets

- [ ] Five to ten small repositories or fixtures with known bugs
- [ ] Expected bug location for each fixture
- [ ] Expected fix or passing-test result
- [ ] Baseline comparison using raw stack traces only
- [ ] Measurements for:
  - [ ] Bug localization accuracy
  - [ ] Patch test-pass rate
  - [ ] False diagnosis rate
  - [ ] Time to first useful diagnosis
  - [ ] Number of model calls per repair

## 7. Demo and deployment assets

- [ ] One reliable seeded repository with a failing test
- [ ] A working local demo
- [ ] A public hosted demo, if deployment is stable
- [ ] Backup recording of the demo
- [ ] Demo script under three minutes
- [ ] Screenshots showing diagnosis, diff, and passing tests
- [ ] A short explanation of how Token Factory accelerated the project

## 8. Optional items

- [ ] RTX 4050 laptop for longer evaluation runs or recording
- [ ] Nebius Serverless Jobs for asynchronous test execution
- [ ] Additional language support such as JavaScript or TypeScript
- [ ] GitHub pull-request integration
- [ ] Local small-model fallback
- [ ] Containerized sandbox for stronger isolation

## 9. Explicitly not required for the MVP

- [ ] Local Nemotron hosting
- [ ] CUDA installation on the Omarchy laptop
- [ ] Fine-tuning
- [ ] Multi-language support
- [ ] Autonomous GitHub pushing
- [ ] A complex multi-agent framework
