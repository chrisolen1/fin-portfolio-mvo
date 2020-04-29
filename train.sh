nohup python3 -u training_and_prediction.py --batch_size 5 \
        --n_timesteps 10 \
        --n_epochs 5 \
        --look_ahead_time 1 \
        --validation_split 0.1 \
        --burn_in_length 200 \
        --burn_in_epochs 50 \
        --delta 1.5 \
        --min_weight 0.01 \
        --vol_window 10 > logs/training_logs.txt 2>&1 &
