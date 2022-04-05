

import numpy as np
import pandas as pd

def generate_users(number_of_users = 1000, mu1 = 4, sigma1 = 2, mu2 = 5, sigma2 = 3):

    # The purpose of this file is to generate a list of users with unique id's and 
    # assign them an average number of interactions for the two software versions

    np.random.seed(100)

    user_parameters = pd.DataFrame()

    # Generate user_id's that are non-sequential and give them an average number of interactions
    # for each version
    user_parameters['UID'] = (np.random.random(size = number_of_users)*10*number_of_users).astype(int)
    user_parameters['avg_orig'] = np.random.normal(loc = mu1, scale = sigma1, size = number_of_users)
    user_parameters['avg_test'] = np.random.normal(loc = mu2, scale = sigma2, size = number_of_users)

    return user_parameters


