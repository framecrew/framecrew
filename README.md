# FrameCrew

[![CI](https://github.com/framecrew/framecrew/actions/workflows/ci.yml/badge.svg)](https://github.com/framecrew/framecrew/actions/workflows/ci.yml)

**An experimental Hermes-based, multi-agent video-editing workflow with staged execution and a QC gate.**

FrameCrew defines a 13-skill video-production workflow for [Hermes](https://hermes-agent.nousresearch.com/): footage intake, edit stages, audio, enhancement, quality checks, and delivery. It uses Markdown agent instructions, shell scripts, FFmpeg, and configurable presets. **The complete footage-to-delivery workflow has not yet been validated end to end on real footage.**

> **Status: experimental / pre-v0.1.0.** Existing CI runs synthetic fixture generation, a basic FFmpeg cutting test, structural skill linting, and a QC pass/fail test. The `e2e_smoke.sh` script **re-runs these tests**; it is not a full Hermes-orchestrated end-to-end test. Agent behavior, Telegram confirmation, real-footage output quality, and DaVinci project delivery still need manual integration testing. See [Testing and limitations](#testing-and-limitations).

---

## Quick setup (experimental)

```bash
git clone https://github.com/framecrew/framecrew.git && cd framecrew
cp .env.example .env            # add your OPENAI_API_KEY
./install.sh                    # deps + Hermes routing + loads all 13 skills
```
Then use the kickoff instructions in [`KICKOFF.md`](KICKOFF.md) to attempt an integration run. **This is an experimental workflow, not a verified one-command editing product.**

---

## 🚀 Getting started (guided)

New to this? Follow along — it's four steps and you only do steps 1–3 once.

### Step 1 — Install the prerequisites

You need these on your Mac (Apple Silicon):

- **[Hermes](https://hermes-agent.nousresearch.com/)** — the agent runtime that runs the crew
- **FFmpeg 8+, Whisper, PySceneDetect, ImageMagick, Real-ESRGAN, rembg** — the media tools
- **DaVinci Resolve Studio** — for the final project delivery (Studio only; the free version can't script)
- An **LLM API key** from any OpenAI-compatible provider (OpenAI, OpenRouter, Together, …)
- A **Telegram bot** (optional) if you want the drop-and-confirm-on-your-phone flow

The installer now fails on Homebrew/Python package-install errors and installs Python dependencies into the repository-local `.venv` rather than the system Python. Run `./scripts/doctor.sh` afterward to identify missing tools. **A clean installation has not yet been independently verified on a fresh Mac.**

### Step 2 — Get the code and add your key

```bash
git clone https://github.com/framecrew/framecrew.git
cd framecrew
cp .env.example .env
```
Open `.env` and paste your `OPENAI_API_KEY` (and Telegram token if you have one).

### Step 3 — Run the one-shot installer

```bash
./install.sh
```
This installs the media tools, writes FrameCrew's model-routing rules into Hermes, loads all 13 agent skills into `~/.hermes/skills/video`, and creates your `~/FrameCrew/Projects` and `Templates` folders. Then run the environment check:

```bash
./scripts/doctor.sh
```
Check the result carefully: missing dependencies are reported, and the doctor is **not** a full functional verification of agent orchestration or delivered video.

### Step 4 — Wake the crew (single kickoff prompt)

Send the kickoff prompt from [`KICKOFF.md`](KICKOFF.md) to Hermes **once**. It loads every skill, applies the routing rules, and starts the Watcher agent listening on your Projects folder.

### Intended workflow (not yet end-to-end validated)

1. Make a folder in `~/FrameCrew/Projects/<ProjectName>/` and drop all your footage in.
2. Copy a template from `~/FrameCrew/Templates/`, fill in the event details, and drop it in as `event.txt` **last** — that's your "go" signal.
3. Hermes messages you: *"New job detected — start pipeline?"* Reply **Yes**.
4. If orchestration and delivery complete successfully, inspect the MP4 and DaVinci project. This step is not yet validated on real footage.

Everything is config-driven — your brand colors, fonts, folder paths, per-event-type style presets, and loudness targets all live in `config/framecrew.yaml`, so you can make it sound and look like *your* studio.

## How it works

The Editor Manager reads your `event.txt`, picks the style preset for the event type, and runs the crew in strict order — one agent at a time, each waiting for the last to finish:

`Watcher → Intake → (Cut → Trim → Color → Titles → Transitions) → Audio → Enhancement → QC → Delivery`

The agent instructions specify a Kanban card, a QC gate, and re-running failed stages. The current CI validates a limited QC fixture check, **not** those orchestration and recovery behaviors in Hermes.

## Technical overview

For a concise review of architecture, evidence, risks, and acceptance criteria, see [Technical Overview](docs/TECHNICAL_OVERVIEW.md).

## Testing and limitations

### What the current CI checks

The [GitHub Actions workflow](.github/workflows/ci.yml) runs on macOS and invokes:

- `tests/lint_skills.sh`: checks the exact 13-skill inventory, Markdown skill structure, and scans selected directories for a small set of secret-like patterns. **This is not comprehensive secret scanning.**
- `tests/fixtures/make_fixtures.sh`: generates synthetic video/audio fixtures with FFmpeg.
- `tests/test_cutting.sh`: concatenates generated clips and verifies that input files were not modified. This directly tests an FFmpeg command, **not the cutting agent's instructions or Hermes execution**.
- `tests/test_qc.sh`: exercises a test-local QC function against complete and missing-LUT fixtures. This **does not execute the QC agent**.
- `tests/e2e_smoke.sh`: re-runs lint, cutting, and QC checks in a mock-mode script; it does not traverse the 13-agent pipeline.

### Not yet verified

- Real-footage multi-agent execution from Watcher to Delivery
- Hermes runtime compatibility, persistent folder watching, and Telegram confirmation
- Stage-specific recovery and end-to-end Kanban updates
- Real output quality, audio processing, enhancement, and DaVinci Resolve Studio project generation
- A clean, repeatable dependency installation on a fresh Mac

### Security and setup cautions

- Do not commit `.env`, API tokens, raw footage, or private project data.
- Review `install.sh` before running. It invokes Homebrew, creates `.venv`, and installs Python media dependencies that can be substantial. It now fails if package installation fails, but full macOS installation remains unverified.
- Run `./scripts/doctor.sh` after setup. A successful environment check does not establish that a finished video can be produced.
- Only use footage and music for which you have the necessary rights.

### To reach v0.1.0

A release candidate should include a documented real-footage acceptance run: clean installation; Hermes agent startup; confirmation flow; all stage outputs; a deliberately induced QC failure and recovery; delivered MP4/Resolve project; and captured run logs with secrets removed.

---

## Requirements

- macOS on Apple Silicon (built and tested on M2)
- Hermes (agent runtime)
- An LLM API key — any **OpenAI-compatible** endpoint
- FFmpeg 8+, Whisper, PySceneDetect, ImageMagick, Real-ESRGAN, rembg
- DaVinci Resolve **Studio** (scripting API is Studio-only)
- A Telegram bot token — optional, for the phone confirm flow

## Project layout

```
framecrew/
├── README.md
├── KICKOFF.md                   # the single prompt that wakes the crew
├── LICENSE
├── .env.example
├── config/
│   └── framecrew.example.yaml   # brand + routing + style presets
├── memories/
│   └── model-routing.md         # Hermes routing rules (installed into ~/.hermes)
├── install.sh                   # one-shot installer
├── scripts/                     # doctor, hermes setup, skill install
├── skills/video/                # the 13 agent skill files Hermes loads
├── templates/                   # event.txt templates per event type
└── tests/                       # synthetic fixtures + per-agent tests
```

## Roadmap

- [ ] Genericize skills fully against real footage
- [x] One-shot installer + environment doctor implemented (fresh-Mac verification pending)
- [x] Single kickoff prompt for Hermes
- [x] Synthetic-fixture test harness + per-agent tests + QC fail-test
- [x] CI (macOS runner)
- [ ] Full real-footage integration and acceptance run → tag `v0.1.0` (API-first)
- [ ] Optional local-model routing (Ollama) as a cost-saving alternative — post-v0.1.0
- [ ] Standalone / runtime-agnostic mode — later

## License

[MIT](LICENSE)
