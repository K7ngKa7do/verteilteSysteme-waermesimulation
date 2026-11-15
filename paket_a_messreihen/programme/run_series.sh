#!/bin/bash
# Aufruf: bash run_series.sh HOSTLISTE AUSGABE.csv "N-Werte" "P-Werte" WIEDERHOLUNGEN
HOSTS=$1; OUT=$2; NS=$3; PS=$4; REP=$5
PROG=~/waerme/kadan/heat_csv.py
[ -f "$OUT" ] || echo "datum,P,N,schritte,zeit_s,komm_max_s,summe" > "$OUT"
for N in $NS; do
  for P in $PS; do
    for i in $(seq 1 $REP); do
      mpirun --hostfile "$HOSTS" -np $P --map-by slot ~/venv/bin/python $PROG $N 200 < /dev/null 2>&1 \
        | grep -E '^[0-9]+,' | sed "s/^/$(date +%F_%T),/" >> "$OUT"
    done
  done
done
echo "fertig: $(wc -l < "$OUT") Zeilen in $OUT"
