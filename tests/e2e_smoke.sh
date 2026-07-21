#!/usr/bin/env bash
# End-to-end smoke test in mock mode: exercises the testable pipeline steps.
set -euo pipefail
export FRAMECREW_TEST_MODE=1

echo "== FrameCrew e2e smoke (mock mode) =="
bash tests/lint_skills.sh
bash tests/test_cutting.sh
bash tests/test_qc.sh
echo "== e2e smoke complete: all checks passed =="
