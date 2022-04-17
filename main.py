import argparse
import configparser
import json
from pandas.io.json import json_normalize
import pickle
import pandas as pd
import numpy as np
import warnings 
warnings.filterwarnings("ignore")
import gc
import time
import crack, utils

# !pip3 install pandas==0.25.1
def training_args():
    parser=argparse.ArgumentParser(description='Generate_Set')
    
    #Set folder
    parser.add_argument('--folder_data', default='data', type=str,
                        help="Set the folder path")
 
     
    #Elastic parameters
    parser.add_argument('--E', default=71.7e9, type=float,
                        help="Young's modulus of the structure")
    parser.add_argument('--nu', default=0.33, type=float,
                        help="Poisson's ratio of the structure")
    
    #Strain field parameters
    parser.add_argument('--sigma_inf', default=78.6e6, type=float,
                        help="Maximum stress intensity")
    parser.add_argument('--K_IC', default=19.7, type=float,
                        help="Fracture toughness of the structure")
    
    #Strain gauges
    parser.add_argument('--nb_gauges', default=3, type=int,
                        help="Number of gauges")
    parser.add_argument('--x_gauge', default=(0.003, 0.014, 0.025), type=tuple,
                        help="x position of the gauges placed")
    parser.add_argument('--y_gauge', default=(0.014, 0.014, 0.014), type=tuple,
                        help="y position of the gauges placed")
    parser.add_argument('--theta_gauges', default=45, type=float,
                        help="Angle of the gauges placed")
  
    #Initialization parameters
    parser.add_argument('--a_0_mean', default=0.001, type=float,
                        help="Initial half crack length mean in [m]")
    parser.add_argument('--m_mean', default=3.5, type=float,
                        help="m mean")
    parser.add_argument('--m_std', default=0.125, type=float,
                        help="m std") 
    parser.add_argument('--C_mean', default=1e-10, type=float,
                        help="C mean")
    
    #Sampling
    parser.add_argument('--n_train', default=1000, type=int,
                        help="Number of training structures")
    parser.add_argument('--n_val', default=100, type=int,
                        help="Number of validation structures")
    parser.add_argument('--n_test', default=100, type=int,
                        help="Number of testing structures") 
    parser.add_argument('--delta_k', default=500, type=int,
                        help="Data collection interval")
 
    parser.add_argument('--lb_star', default=0.33, type=float,
                        help="lower boundary (used for generating t* for the test set)") 
    parser.add_argument('--ub_star', default=0.95, type=float,
                        help="upper boundary (used for generating t* for the test set)")

    args=parser.parse_args()
    return args

args = training_args()



# Set Elastic parameters
E = args.E
nu = args.nu

# Set Gauges Placement
x_gauge = args.x_gauge
y_gauge = args.y_gauge
nb_gauges = args.nb_gauges
theta_gauge = args.theta_gauges


# Set Crack Data
a_0_mean = args.a_0_mean
a_0_std = a_0_mean*0.125  # Standard deviation of a_0 corresponding to a CoV of a0_mean, here CoV = 0.125
C_mean = args.C_mean # Value of Paris law constant C representing its log mean (exp(mean(log(C))))
C_std = C_mean*(8e3-1)/(2+2*8e3) #ratio 95%
m_mean = args.m_mean # Paris law exponent
m_std = args.m_std #Standard deviation of Paris law exponent (1/1.96, correspondig to having 95% confidence interval at +- 1



# [Load]
K_IC = args.K_IC #Fracture toughness of the structure 
sigma_inf = args.sigma_inf 
sigma_0 = 0 # Minimum load in MPa
delta_sigma = sigma_inf-sigma_0 # Difference between maximum and minimum load in MPa
a_crit = (K_IC/(delta_sigma*1e-6*np.sqrt(np.pi)))**2  #(half) crack size at failure time T


# [Sampling]
n_train = args.n_train # Number of "experiments" for training
n_validation = args.n_val # Number of "experiments" for validation
n_test = args.n_test# Number of "experiments" for testing

#other parameters
thinning = args.delta_k # Take values only every `thinning` cycles
lb_tstar = args.lb_star #lower boundary
ub_tstar = args.ub_star #upper boundary


if __name__ == "__main__":
    
    # set folder
    print('Create folder...', end = ' ')
    folder_data = args.folder_data
    import os
    os.mkdir(folder_data)
    print('Done.')
    
    #save the args
    print('Save the args...', end = ' ')
    f = open(folder_data+"/args.txt", "w+")
    f.write(str(args))
    f.close()
    print('Done.')
    
    #Generate set
    print('Generate datasets...')
    
    if n_train >= 1 : 
        print('\nTraining set:')
        training_set = utils.gen_dataset('train', x_gauge, y_gauge, theta_gauge, delta_sigma, E, nu, a_0_mean, a_0_std, a_crit, C_mean, C_std, m_mean, m_std, n_train, thinning)
        training_set.to_pickle(folder_data + '/training_set', protocol = pickle.HIGHEST_PROTOCOL)

    if n_validation >= 1 : 
        print('\nValidation set:')
        validation_set = utils.gen_dataset('train', x_gauge, y_gauge, theta_gauge, delta_sigma, E, nu, a_0_mean, a_0_std, a_crit, C_mean, C_std, m_mean, m_std, n_train, thinning)
        validation_set.to_pickle(folder_data + '/validation_set', protocol = pickle.HIGHEST_PROTOCOL)

    if n_test >= 1 : 
        print('\nTest set:')
        test_set = utils.gen_dataset('test', x_gauge, y_gauge, theta_gauge, delta_sigma, E, nu, a_0_mean, a_0_std,a_crit, C_mean, C_std, m_mean, m_std, n_test, thinning)
        test_set['t_star'] = 0 #t* which is the size of the sequence (in number of cycles) available for the testing set
        test_set['t_star'] = (np.random.uniform(low=lb_tstar, high=ub_tstar, size=(test_set.shape[0],)) * test_set.nb_cycles.values).astype(int)
        test_set.to_pickle(folder_data + '/test_set', protocol = pickle.HIGHEST_PROTOCOL)
    print("Done.")

    #Structuring into dataframes
    print("Structuring the datasets...")
    cols = ['ID', 'cycle'] +  ['gauge' + str(i+1) for i in range(nb_gauges)] +  ['RUL'] #set columns for the datasets
    #set the stop_tstar args to True if the sequences should be incomplete (for example for the test set)
    print('\nTraining set:')
    utils.build_dataset(training_set,    cols,  nb_gauges = nb_gauges, stop_tstar = False, thinning = thinning).to_pickle(folder_data + '/data_train')
    print('\nValidation set:')
    utils.build_dataset(validation_set,  cols,  nb_gauges = nb_gauges, stop_tstar = False, thinning = thinning).to_pickle(folder_data + '/data_val')
    print('\nTest set:')
    utils.build_dataset(test_set,        cols,  nb_gauges = nb_gauges, stop_tstar = True,  thinning = thinning).to_pickle(folder_data + '/data_test')
    print('Done.')
