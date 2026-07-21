# Contributing to FrameCrew

Thanks for helping build FrameCrew.

## Ground rules

- **No secrets, ever.** No API keys, tokens, personal paths, or real footage in commits. `tests/lint_skills.sh` scans for these and CI will fail if found.
- **Config-driven, not hardcoded.** Brand values, paths, and style presets live in `config/framecrew.yaml`. Skills read from config.
- **Every agent stays green.** If you add or change an agent, add/adjust its test under `tests/` and keep the suite passing.

## Local checks before a PR

```bash
./scripts/doctor.sh        # environment
bash tests/lint_skills.sh  # structure + secret scan
bash tests/e2e_smoke.sh    # synthetic end-to-end (mock mode)
```

## What CI covers vs. not

CI (macOS runner) runs the lint, synthetic fixtures, per-agent tests, the QC pass/fail test, and the mock-mode smoke test. It does **not** cover the Telegram trigger, DaVinci Resolve project build, or real S-Log footage — those are validated by the manual acceptance checklist before a release.
