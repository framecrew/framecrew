# FrameCrew

[![CI](https://github.com/framecrew/framecrew/actions/workflows/ci.yml/badge.svg)](https://github.com/framecrew/framecrew/actions/workflows/ci.yml)

**A single-shot Hermes agent that edits your footage for you. Drop clips, get a finished cut.**

FrameCrew is a crew of video-editing agents that run on [Hermes](https://github.com/hermes). You drop your footage into a folder, add a short `event.txt` brief, and confirm on your phone — then the crew cuts, trims, colors, titles, adds transitions, cleans audio, enhances stills, runs QC, and delivers a finished MP4 plus a ready-to-open DaVinci Resolve project. All in one shot.

> ⚠️ **Status: early / work in progress.** The media work runs on your own machine (FFmpeg, Whisper, DaVinci Resolve); the agents reason through a hosted LLM API. Building toward a verified `v0.1.0`. See [Roadmap](#roadmap).

---

## ⚡ Experienced? The 30-second version

```bash
git clone https://github.com/framecrew/framecrew.git && cd framecrew
cp .env.example .env            # add your OPENAI_API_KEY
./install.sh                    # deps + Hermes routing + loads all 13 skills
```
Then paste the kickoff prompt from [`KICKOFF.md`](KICKOFF.md) to Hermes once. Drop footage + `event.txt`, reply **Yes**, done.

---

## 🚀 Getting started (guided)

New to this? Follow along — it's four steps and you only do steps 1–3 once.

### Step 1 — Install the prerequisites

You need these on your Mac (Apple Silicon):

- **[Hermes](https://github.com/hermes)** — the agent runtime that runs the crew
- **FFmpeg 8+, Whisper, PySceneDetect, ImageMagick, Real-ESRGAN, rembg** — the media tools
- **DaVinci Resolve Studio** — for the final project delivery (Studio only; the free version can't script)
- An **LLM API key** from any OpenAI-compatible provider (OpenAI, OpenRouter, Together, …)
- A **Telegram bot** (optional) if you want the drop-and-confirm-on-your-phone flow

Don't worry about installing each media tool by hand — `install.sh` does that in Step 3.

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
Everything should show ✓.

### Step 4 — Wake the crew (single kickoff prompt)

Send the kickoff prompt from [`KICKOFF.md`](KICKOFF.md) to Hermes **once**. It loads every skill, applies the routing rules, and starts the Watcher agent listening on your Projects folder.

### That's it — your daily workflow

1. Make a folder in `~/FrameCrew/Projects/<ProjectName>/` and drop all your footage in.
2. Copy a template from `~/FrameCrew/Templates/`, fill in the event details, and drop it in as `event.txt` **last** — that's your "go" signal.
3. Hermes messages you: *"New job detected — start pipeline?"* Reply **Yes**.
4. When it's done, open the finished MP4 or the DaVinci project in the folder.

Everything is config-driven — your brand colors, fonts, folder paths, per-event-type style presets, and loudness targets all live in `config/framecrew.yaml`, so you can make it sound and look like *your* studio.

## How it works

The Editor Manager reads your `event.txt`, picks the style preset for the event type, and runs the crew in strict order — one agent at a time, each waiting for the last to finish:

`Watcher → Intake → (Cut → Trim → Color → Titles → Transitions) → Audio → Enhancement → QC → Delivery`

A Kanban card tracks the job through every stage, and the QC agent is a hard gate: it rejects with a specific reason (not just "failed") and the manager re-runs only the stage that failed.

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
- [x] One-shot installer + environment doctor
- [x] Single kickoff prompt for Hermes
- [x] Synthetic-fixture test harness + per-agent tests + QC fail-test
- [x] CI (macOS runner)
- [ ] Manual acceptance run → tag `v0.1.0` (API-first)
- [ ] Optional local-model routing (Ollama) as a cost-saving alternative — post-v0.1.0
- [ ] Standalone / runtime-agnostic mode — later

## License

[MIT](LICENSE)
