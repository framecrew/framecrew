# FrameCrew — Technical Overview

**Project:** Experimental multi-agent video automation on Hermes  
**Status:** Pre-v0.1.0; synthetic checks exist, real-footage acceptance is pending  
**Repository:** [framecrew/framecrew](https://github.com/framecrew/framecrew)

## Problem

An event-video edit moves through repeatable stages: footage intake, scene selection, trimming, color, titles, transitions, sound, enhancements, quality checks, and delivery. Each handoff needs an explicit output contract so a failed stage does not silently become the input to the next.

## Design

FrameCrew defines **13 Hermes agent skills**. The [Editor Manager](../skills/video/editor-manager.md) is instructed to run stages serially, with the [Edit Team Lead](../skills/video/edit-team-lead.md) coordinating the five edit stages. Job-specific styling and audio targets live in an example YAML configuration rather than being embedded in each skill.

```text
Watcher (human confirmation)
  → Editor Manager
    → Intake
    → Edit Team Lead: Cut → Trim → Color → Titles → Transitions
    → Audio → Enhancement → QC
    → Delivery (only after QC passes)
```

This is an **intended workflow described in agent instructions**, not proof of an autonomous production run.

## Technology and responsibilities

- **Hermes / LLM orchestration:** Markdown agent instructions and a kickoff prompt
- **Media processing:** FFmpeg/ffprobe, PySceneDetect, Whisper, and optional enhancement utilities
- **Environment:** macOS, shell installer, Python virtual environment, YAML configuration
- **Quality strategy:** Required output artifacts, a rejection path in agent instructions, and synthetic QC fixtures
- **Automation:** GitHub Actions on macOS for static checks and synthetic media tests

## Evidence available today

| Claim | Evidence | Important limitation |
| --- | --- | --- |
| 13 skill definitions | `skills/video/` plus inventory check in `tests/lint_skills.sh` | Having files is not proof they execute in Hermes |
| Synthetic cutting check | `tests/test_cutting.sh` | Runs FFmpeg directly, not the cutting agent |
| Synthetic QC rejection | `tests/test_qc.sh` | Runs a test-local QC function, not the QC agent |
| Mock smoke workflow | `tests/e2e_smoke.sh` | Re-runs checks; does not exercise all agents |
| Agent failure-routing design | Editor Manager and QC instructions | Recovery behavior has not been integration-tested |

## Engineering risks and next acceptance gate

The largest unresolved risk is **integration between LLM-driven instructions and executable media operations**. Additional risks include installation portability, quality and rights of supplied media, DaVinci Resolve Studio scripting integration, and operational observability.

Before calling this an end-to-end video editing product, a test should demonstrate a clean macOS setup; Hermes startup; explicit confirmation; real inputs processed through each stage; a deliberately induced failure and recovery; and successful MP4 and Resolve project outputs. Logs and evidence should not contain credentials or private footage.

## Why this project is relevant to analytics and AI roles

The transferable engineering focus is **orchestration, typed stage outputs, validation gates, failure isolation, and reproducible testing**. The repository demonstrates a concrete attempt to turn a multi-step task into an agent-guided workflow while making the distinction between what is specified, what is tested, and what remains unverified explicit.
