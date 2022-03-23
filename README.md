# Framework_FDPP
FDPP is an open-source framework for generating large synthetic data sets specific to fatigue damage prognostic problems, in particular for an aerospace structure problems (e.g. fuselage panels). 

# Description

The idea behind this project is to propose a framework and software code for synthetically generating large training data sets for a realistic fatigue damage prognostics problem. 

The project is illustrated with a realistic case study on the Jupyter Notebook ``Illustration_CaseStudy.ipynb``, i.e. a RUL estimation problem where the available input data is strain gauge data, and the applicability of some of the most commonly used DL models to address failure prognostics has been studied (RNN, LSTM, GRU, 1D-CNN and TCN), available on the ``models`` directory.

# Setup

Reproducible results are possible using the Keras Tensorflow library. This code was tested on Python 3.8.5, Pandas 0.25.1, Ubuntu 18.04, Anaconda 4.7.11, Tensorflow version 2.3.0, and CUDA 11.0. It requires V100 GPUs.

# Acknowledgements

◦ This work was partially funded by Occitanie region under the Predict project. This funding is gratefully acknowledged. 

◦ This work has been carried out on the supercomputers PANDO (ISAE Supaero, Toulouse) and Olympe (CALMIP, Toulouse, project n°21042). Authors are grateful to ISAE Supaero and CALMIP for the hours allocated to this project.

◦ The authors would like to thank Christian Nitschke for his initial input on modelling the crack growth problem.
