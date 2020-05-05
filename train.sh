nohup python3 -u training_and_prediction.py --batch_size 100 \
        --n_timesteps 30 \
        --n_epochs 50 \
        --look_ahead_time 1 \
        --validation_split 0.2 \
        --burn_in_length 400 \
        --burn_in_epochs 200 \
        --delta 1.5 \
        --min_weight 0.01 \
        --vol_window 30 > logs/training_logs.txt 2>&1 &
