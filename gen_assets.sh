#!/bin/bash
# Generate the three featured artworks, patiently retrying the free route.
cd "$(dirname "$0")" || exit 1
mkdir -p assets

p_bridges="Flat editorial newspaper illustration, aerial view at night: a wide dark river crossed by three long bridges seen from above at an angle, one bridge broken in the middle, thin red missile trails arcing in the sky, small fires glowing on both banks, city lights as tiny dots, muted flat colours, clean simple shapes, no text, no words, no letters, no logos"
p_cyclone="Flat editorial newspaper illustration, view from the sea looking toward land: a fishing village coastline, a vast white cyclone spiral filling the sky, waves with white crests rolling toward the shore, palm trees bent sideways, fishing boats hauled up on the sand, muted flat colours, clean simple shapes, no text, no words, no letters, no logos"
p_cop31="Flat editorial newspaper illustration: the exterior of a modern glass conference centre at dusk, a long row of national flags on tall poles in front, delegates as small silhouettes arriving with briefcases, mountains behind the building, muted flat colours, clean simple shapes, no text, no words, no letters, no logos"

for round in $(seq 1 60); do
  todo=0
  for n in bridges cyclone cop31; do
    if [ ! -s "assets/$n.png" ]; then
      todo=1
      eval "p=\$p_$n"
      echo "TRY $n round $round $(date +%T)"
      python3 /home/hermes/recraft_gen.py "$p" "assets/$n.png" 2>&1 | tail -1
    fi
  done
  if [ $todo -eq 0 ]; then echo "ALLDONE $(date +%T)"; break; fi
  sleep 90
done
ls -l assets/
