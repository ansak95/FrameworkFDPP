#!/bin/sh
python main.py               --folder_data            data \
                             --E                      71.7e9 \
                             --nu                     0.33 \
                             --sigma_inf              78.6e6 \
                             --K_IC                   19.7 \
                             --nb_gauges              3 \
                             --x_gauge                0.003 0.014 0.025 \
                             --y_gauge                0.014 0.014 0.014  \
                             --theta_gauges           45 \
                             --a_0_mean               0.001 \
                             --m_mean                 3.5 \
                             --m_std                  0.125 \
                             --C_mean                 1e-10 \
                             --n_train                1000  \
                             --n_val                  100 \
                             --n_test                 100 \
                             --delta_k                500 \
                             --lb_star                0.33 \
                             --ub_star                0.95 
