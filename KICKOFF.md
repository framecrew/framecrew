# FrameCrew — Kickoff Prompt

Send this to Hermes after running the [FrameCrew installer](README.md). Launch Hermes from the FrameCrew checkout so it can find the local config and media tools.

Copy everything in the box below:

---

```
You are running FrameCrew, a video-editing agent crew.

1. Load the installed FrameCrew skills by name (watcher-agent, editor-manager,
   intake-agent, edit-team-lead, cutting-agent, trimming-agent, color-agent,
   titles-agent, transitions-agent, audio-agent, enhancement-agent, qc-agent,
   delivery-agent). Report any missing skill.
2. Read the FrameCrew model routing notes in memories/model-routing.md.
3. Read config/framecrew.yaml for brand, paths, and event-style presets.
4. Activate the Watcher agent on the projects_root from config and keep watching.
5. When a new folder gets an event.txt, run the stability checks, then message me
   "New job detected: <name> — <N> clips. Start pipeline?" and wait for my "Yes"
   before doing anything else.

Reply with the list of skills you loaded and confirm the Watcher is active.
```

---

## What to expect back

Verify folder detection with a test project before relying on the Watcher for unattended jobs. A reply alone does not prove that monitoring continues after the session ends.

## Re-running

If Hermes gets slow or you restart your machine, just send this prompt again in a fresh conversation. It's safe to re-run any time.
