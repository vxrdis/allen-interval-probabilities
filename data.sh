#!/bin/zsh

echo "Launching 10 million trial runs for all 7 (pBorn, pDie) pairs..."

SEEDS=(42 43 44 45 46 47 48)
PBORNS=(0.5 0.1 0.01 0.1 0.01 0.2 0.1)
PDIES=(0.5 0.1 0.01 0.2 0.1 0.1 0.01)

for i in {1..7}; do
    IDX=$((i - 1))
    PB=${PBORNS[$i]}
    PD=${PDIES[$i]}
    SEED=${SEEDS[$i]}

    echo "-----------------------------"
    echo "Running pBorn=$PB, pDie=$PD (seed=$SEED)"
    echo "-----------------------------"

    # Run global simulation
    python3 batch_runner.py \
        --pBorn $PB \
        --pDie $PD \
        --trials 10000000 \
        --output sim_p${PB}_q${PD}.json \
        --quiet \
        --seed $SEED

    # Run composition analysis
    python3 comp_runner.py \
        --pBorn $PB \
        --pDie $PD \
        --trials 10000000 \
        --limit 10000000 \
        --output comp_p${PB}_q${PD}.json \
        --quiet \
        --seed $SEED
done

echo "\n✅ All simulations complete. Results saved to ./sim_*.json and ./comp_*.json"