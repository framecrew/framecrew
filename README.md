# FrameCrew

**Drop your footage. Get a finished edit.**

FrameCrew is a local-first, agent-driven video editing pipeline. You drop your clips into a project folder, add a short `event.txt` brief, confirm on your phone, and a crew of agents handles the rest — cut, trim, color, titles, transitions, audio, enhancement, QC, and delivery — producing a finished MP4 plus a ready-to-open DaVinci Resolve project.

> ⚠️ **Status: early / work in progress.** The media pipeline runs on your own machine (FFmpeg, Whisper, DaVinci Resolve); agent reasoning runs through a hosted LLM API. This repo is being built toward a verified `v0.1.0` release. See [Roadmap](#roadmap).

---

## How it works

1. Create a project folder and drop all footage into it.
2. Copy an `event.txt` template, fill in the event details, and drop it in **last** — this is your ready signal.
3. A watcher detects the folder, verifies all files finished copying, and pings you to confirm.
4. On your **Yes**, the agent crew runs end to end and saves the finished edit, LUT, transcripts, and a DaVinci project into the folder.

Everything is config-driven — brand colors, fonts, folder paths, per-event-type style presets, and loudness targets all live in `config/framecrew.yaml`, so anyone can rebrand it to their own studio.

## Quick start

```bash
git clone https://github.com/framecrew/framecrew.git
cd framecrew
cp config/framecrew.example.yaml config/framecrew.yaml   # edit for your brand
cp .env.example .env                                      # add your API key (+ Telegram token)
./install.sh                                              # install deps + create folders
./scripts/doctor.sh                                       # verify the environment
```

## Requirements

- macOS on Apple Silicon (built and tested on M2)
- An LLM API key — any **OpenAI-compatible** endpoint (OpenAI, OpenRouter, Together, a local proxy, …)
- FFmpeg 8+, Whisper, PySceneDetect, ImageMagick, Real-ESRGAN, rembg
- DaVinci Resolve **Studio** (the scripting API used for project delivery is Studio-only)
- A Telegram bot token (for the drop-and-confirm workflow) — optional but recommended

## What's verified vs. manual

Mechanical steps (tool presence, the cut/trim/color/titles/audio processing, skill-file structure, and the QC gate) are covered by automated tests that generate their own synthetic clips — no real footage needed. Integrations that a CI runner can't touch (Telegram trigger, DaVinci Resolve build, real S-Log footage) are validated by a manual acceptance checklist before each release.

## Project layout

```
framecrew/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── config/
│   └── framecrew.example.yaml   # brand + routing + style presets
├── install.sh                   # one-shot installer (coming soon)
├── scripts/                     # doctor, ollama setup, skill install
├── skills/video/                # the agent skill files
├── templates/                   # event.txt templates per event type
└── tests/                       # synthetic fixtures + per-agent tests
```

## Roadmap

- [ ] Genericize skills to read from config (remove hardcoded paths/brand)
- [ ] Installer + environment doctor
- [ ] Synthetic-fixture test harness + per-agent tests + QC fail-test
- [ ] CI (macOS runner)
- [ ] Layered docs (quick-start + full walkthrough)
- [ ] Manual acceptance run → tag `v0.1.0` (API-first)
- [ ] Optional local-model routing (Ollama) as a cost-saving alternative — post-v0.1.0

## License

[MIT](LICENSE)
