# FrameCrew — Kickoff Prompt

Send this **once** to Hermes (Telegram or terminal) after running `./install.sh`. It wakes the whole crew in a single shot.

Copy everything in the box below:

---

```
You are running FrameCrew, a video-editing agent crew.

1. Load every skill in ~/.hermes/skills/video (watcher, editor-manager, intake,
   edit-team-lead, cutting, trimming, color, titles, transitions, audio,
   enhancement, qc, delivery). Confirm each one loaded by name.
2. Apply the routing rules in ~/.hermes/memories/user/model-routing.md.
3. Read config/framecrew.yaml for brand, paths, and event-style presets.
4. Activate the Watcher agent on the projects_root from config and keep watching.
5. When a new folder gets an event.txt, run the stability checks, then message me
   "New job detected: <name> — <N> clips. Start pipeline?" and wait for my "Yes"
   before doing anything else.

Reply with the list of skills you loaded and confirm the Watcher is active.
```

---

## What to expect back

Hermes should reply with all 13 skills loaded and confirm the Watcher is listening on your `~/FrameCrew/Projects` folder. From then on you never touch this prompt again — just drop footage + `event.txt` and reply **Yes**.

## Re-running

If Hermes gets slow or you restart your machine, just send this prompt again in a fresh conversation. It's safe to re-run any time.
