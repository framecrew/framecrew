#!/usr/bin/env bash
# Generate synthetic test footage so the suite needs no real assets.
set -euo pipefail
DIR="${1:-tests/.work/IntakeTest}"
rm -rf "$DIR"; mkdir -p "$DIR/raw"

# 3 short clips: color bars + tone
for i in 1 2 3; do
  ffmpeg -y -f lavfi -i "testsrc=duration=3:size=320x240:rate=25" \
         -f lavfi -i "sine=frequency=440:duration=3" \
         -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest \
         "$DIR/raw/clip_$i.mp4" >/dev/null 2>&1
done

# a silent clip and a low-res still (for the enhancement agent)
ffmpeg -y -f lavfi -i "color=c=black:s=320x240:d=2" -c:v libx264 -pix_fmt yuv420p "$DIR/raw/silent.mp4" >/dev/null 2>&1
ffmpeg -y -f lavfi -i "color=c=0xD4AF37:s=640x360:d=1" -frames:v 1 "$DIR/still_01.jpg" >/dev/null 2>&1

cat > "$DIR/event.txt" <<'EOF'
# FrameCrew Event Brief
Event_Type: Wedding
Target_Length: 0-1 minutes
Output_Format: 1080p_MP4
Audio_Spec: web_delivery
Opening_Title: Fixture Test
Lower_Thirds: No
EOF

echo "fixtures created in $DIR"
