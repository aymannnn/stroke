import numpy.random as rng


def create_random_sets(random_set_options):
    '''
    Retuns a list of parameter sets, in the form of tuples that you can unpack
    and pass into the run_model function
    '''
    parameter_sets = []
    while len(parameter_sets) < random_set_options['Number of Random Sets']:
        # Note that randint is a <= x <= b
        current_set = {}
        if random_set_options['sex'] is None:
            current_set['sex'] = rng.randint(0, 1)
        else:
            current_set['sex'] = random_set_options['sex']
        if random_set_options['age'] is None:
            current_set['age'] = rng.randint(30, 80)
        else:
            current_set['age'] = random_set_options['age']
        if random_set_options['RACE'] is None:
            current_set['RACE'] = rng.randint(0, 9)
        else:
            current_set['RACE'] = random_set_options['RACE']
        if random_set_options['time_since_symptoms'] is None:
            current_set['time_since_symptoms'] = rng.uniform(10, 100)
        else:
            current_set['time_since_symptoms'] = random_set_options[
                'time_since_symptoms']
        # have to set time to primary before time to comprehensive
        if random_set_options['time_to_primary'] is None:
            current_set['time_to_primary'] = rng.uniform(10, 60)
        else:
            current_set['time_to_primary'] = random_set_options[
                'time_to_primary']
        if random_set_options['time_to_comprehensive'] is None:
            current_set['time_to_comprehensive'] = rng.uniform(
                current_set['time_to_primary'], 120)
        else:
            current_set['time_to_comprehensive'] = random_set_options[
                'time_to_comprehensive']
        if random_set_options['transfer_time'] is None:
            current_set['transfer_time'] = rng.uniform(
                current_set['time_to_comprehensive'] -
                current_set['time_to_primary'],
                current_set['time_to_comprehensive'] +
                current_set['time_to_primary'])
        else:
            current_set['transfer_time'] = random_set_options['transfer_time']
        parameter_sets.append(current_set)
    print('Random sets have been generated')
    return parameter_sets