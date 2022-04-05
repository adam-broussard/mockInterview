

import numpy as np
import pandas as pd
from tqdm import tqdm


def generate_users():

    user_parameters = generate_user_parameters()
    clean_data = create_clean_user_data(user_parameters)
    noisy_data = add_noise(clean_data)


def generate_user_parameters(number_of_users = 1000, mu1 = 4, sigma1 = 2, mu2 = 5, sigma2 = 3):

    # The purpose of this file is to generate a list of users with unique id's and 
    # assign them an average number of interactions for the two software versions

    np.random.seed(100)

    user_parameters = pd.DataFrame()

    # Generate user_id's that are non-sequential and give them an average number of interactions
    # for each version
    user_parameters['UID'] = (np.random.random(size = number_of_users)*10*number_of_users).astype(int)
    user_parameters['avg_orig'] = np.clip(np.random.normal(loc = mu1, scale = sigma1, size = number_of_users), 0.1, np.inf)
    user_parameters['avg_test'] = np.clip(np.random.normal(loc = mu2, scale = sigma2, size = number_of_users), 0.1, np.inf)

    return user_parameters


def create_clean_user_data(user_parameters, total_logins = 50000):

    np.random.seed(101)

    # Create a baseline dataframe that contains user interactions

    # Set the number of times each user logs in

    unique_users = np.unique(user_parameters['UID'])
    number_of_users = len(unique_users)
    user_logins = np.random.poisson(lam = total_logins / number_of_users, size = number_of_users)

    # Create random login times in 2020 and 2021 for each user
    login_times = np.hstack([1584803805 + (np.random.random(size = this_login_num) * 86400*365).astype(int) for this_login_num in user_logins])
    user_ids = np.hstack([[this_user,]*this_login_num for this_user, this_login_num in zip(unique_users, user_logins)])

    userdata = pd.DataFrame()
    userdata['UID'] = user_ids
    userdata['timestamp'] = pd.to_datetime(login_times, unit = 's')
    userdata['msg'] = 'Login'
    userdata = userdata.sort_values('timestamp').reset_index(drop = True)

    orig_userdata = userdata.loc[:int(len(userdata)/2)]
    test_userdata = userdata.loc[int(len(userdata)/2):]

    # Generate interactions

    new_orig_data = {'UID':[], 'timestamp':[], 'msg':[]}
    new_test_data = {'UID':[], 'timestamp':[], 'msg':[]}

    for this_userdata, new_data, thiskey in zip([orig_userdata, test_userdata], [new_orig_data, new_test_data], ['orig', 'test']):

        for _, this_login in tqdm(this_userdata.iterrows(), total = len(this_userdata)):

            this_user_avg = user_parameters[user_parameters.UID == this_login.UID]['avg_' + thiskey]
            num_interactions = np.random.poisson(lam = this_user_avg)[0]

            # breakpoint()
            times = this_login.timestamp.to_datetime64() + (np.random.random(size = num_interactions + 1) * np.timedelta64(int(86400/2), 's'))
            times.sort()
            msgs = ['record_click' for this_time in times[:-1]]
            msgs.append('Logout')

            new_data['UID'].append([this_login.UID,]*(num_interactions+1))
            new_data['msg'].append(msgs)
            new_data['timestamp'].append(times)

            # temp = pd.DataFrame.from_dict({'timestamp':times, 'msg':msgs, 'UID':[this_login.UID,]*(num_interactions+1)})
            # this_userdata.append(temp, ignore_index = True)

    for thiskey in new_orig_data.keys():
        new_orig_data[thiskey] = np.hstack(new_orig_data[thiskey])
        new_test_data[thiskey] = np.hstack(new_test_data[thiskey])

    # new_orig_data['timestamp'] = np.hstack(new_orig_data['timestamp'])
    # new_test_data['timestamp'] = np.hstack(new_test_data['timestamp'])

    orig_userdata = orig_userdata.append(pd.DataFrame.from_dict(new_orig_data), ignore_index = True)
    test_userdata = test_userdata.append(pd.DataFrame.from_dict(new_test_data), ignore_index = True)

    orig_userdata['version'] = 'orig'
    test_userdata['version'] = 'test'

    return orig_userdata.append(test_userdata, ignore_index = True).sort_values('timestamp').reset_index(drop = True)




def add_noise(userdata, noise_entries = 25000):

    # Adds some bogus entries to the table

    np.random.seed(102)

    min_time = userdata.timestamp.iloc[1].to_datetime64()
    max_time = userdata.timestamp.iloc[-2].to_datetime64()

    random_times = np.random.random(size = noise_entries) * (max_time - min_time) + min_time
    random_times = random_times.astype('datetime64[s]')

    random_users = np.random.choice(np.unique(userdata.UID), size = noise_entries, replace = True)

    random_msgs = [f'Signal_Level_{int(percent):02}' for percent in np.random.random(size = noise_entries)*100.]

    orig_version = ['orig',]*sum(random_times <= userdata.timestamp[userdata.version == 'orig'].iloc[-1].to_datetime64())
    test_version = ['test',]*sum(random_times > userdata.timestamp[userdata.version == 'orig'].iloc[-1].to_datetime64())

    random_version = np.array(orig_version + test_version)

    userdata = userdata.append(pd.DataFrame.from_dict({'timestamp':random_times, 'UID':random_users, 'msg':random_msgs, 'version':random_version}), ignore_index = True)
    userdata = userdata.sort_values('timestamp').reset_index(drop = True)

    return userdata