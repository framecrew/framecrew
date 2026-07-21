# FrameCrew Model Routing Rules

These rules are installed into `~/.hermes/memories/user/model-routing.md` by `install.sh`.

## Default (API-first, v0.1.0)

Use the OpenAI-compatible API configured in `.env` (`OPENAI_API_KEY`, optional `OPENAI_BASE_URL`).

## Rules

1. Routine orchestration — file ops, FFmpeg/PySceneDetect/Whisper execution, Kanban updates, reading skills — use the `fast_model` from `config/framecrew.yaml`.
2. Ambiguous decisions — borderline QC calls, error diagnosis, writing/adjusting a skill — use the `reasoning_model`.
3. Never burn the reasoning model on routine execution.
4. One agent runs at a time; never run two stages in parallel.
5. (Future) A local model (Ollama) may replace the API for routine execution as a cost-saving option — see README roadmap.
