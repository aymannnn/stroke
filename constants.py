'''
Constants are held as functions to make it easier to do sensitivity
analyses later.
'''

import enum
import numpy.random as rng
import inflation

# These don't really match with the rest of the functions in the file but
# it is probably the best place to put these enumerators


class Coordinates(object):
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


class Sex(enum.IntEnum):
    MALE = 0
    FEMALE = 1


class States(enum.IntEnum):
    '''
    Make the model a little easier to read
    '''
    GEN_POP = 0
    MRS_0 = 1
    MRS_1 = 2
    MRS_2 = 3
    MRS_3 = 4
    MRS_4 = 5
    MRS_5 = 6
    MRS_6 = 7
    DEATH = MRS_6
    NUMBER_OF_STATES = 8


def time_limit_tpa():
    return 270


def time_limit_evt():
    return 360


def door_to_needle_primary(base_case=False):
    '''
    Primary data from Gregg Fonarow, not yet published.
    Mean -> 69.17
    STD -> 41.67
    25th -> 47.00
    75th -> 83.00
    Median -> 61.00
    '''
    time = None
    if base_case:
        time = 61.00
    else:
        time = rng.uniform(47.00, 83.00)
    return time


def door_to_needle_comprehensive(base_case=False):
    '''
    Primary data from Gregg Fonarow, not yet published.
    Mean -> 58.92
    STD -> 35.26    
    25th -> 39.00
    75th -> 70.00
    Median -> 52.00
    '''
    time = None
    if base_case:
        time = 52.00
    else:
        time = rng.uniform(39.00, 70.00)
    return time


def door_to_intra_arterial_comprehensive(base_case=False):
    '''
    Primary data from Gregg Fonarow, not yet published.
    Mean -> 174.21
    STD -> 105.00
    25th -> 192.00
    75th -> 83.00
    Median -> 145.00
    '''
    time = None
    if base_case:
        time = 145.00
    else:
        time = rng.uniform(83.00, 192.00)
    return time


class Times(object):
    '''
    Initial setup is with base-case times, but we include a function
    to allow for 
    '''
    door_needle_primary = door_to_needle_primary(True)
    door_needle_comprehensive = door_to_needle_comprehensive(True)
    door_to_intra_arterial = door_to_intra_arterial_comprehensive(True)
    # Assumed right now to be the difference between door to IA
    # and door to needle. This is likely an overestimate of the time
    # to EVT.
    transfer_to_intra_arterial = (door_to_intra_arterial - door_needle_primary)

    @staticmethod
    def get_random_set():
        Times.door_needle_primary = door_to_needle_primary()
        Times.door_needle_comprehensive = door_to_needle_comprehensive()
        Times.door_to_intra_arterial = door_to_intra_arterial_comprehensive()
        # Assumed right now to be the difference between door to IA
        # and door to needle. This is likely an overestimate of the time
        # to EVT.
        Times.transfer_to_intra_arterial = (
            Times.door_to_intra_arterial - Times.door_needle_primary)

    @staticmethod
    def set_to_default():
        Times.door_needle_primary = door_to_needle_primary(True)
        Times.door_needle_comprehensive = door_to_needle_comprehensive(True)
        Times.door_to_intra_arterial = door_to_intra_arterial_comprehensive(
            True)
        Times.transfer_to_intra_arterial = (
            Times.door_to_intra_arterial - Times.door_needle_primary)


def race_to_nihss(race):
    '''
    For now assuming that this is a constant; it was originally with the
    ischemic transitions, but at this point it makes more sense for it to
    just be a constant since it's used for hemorrhagic strokes as well
    '''
    nihss = None
    # Perez de la Ossa et al. Stroke 2014, Schlemm analysis
    if race == 0:
        nihss = 1
    else:
        nihss = -0.39 + 2.39 * race
    return nihss


def no_tx_where_to_go(race):
    '''
    http://stroke.ahajournals.org/content/45/1/87.full
    Okay so this cutoff is based on work by Perez de la Ossa where she finds
    that patients with a RACE >= 5 should be considered as with an LVO,
    and patients with a RACE < 5 are likely not canditates for invasive
    therapies.
    '''

    if race >= 5:
        return "Comprehensive"
    else:
        return "Primary"


def nihss_to_race(nihss):
    '''
    Based on a simple linear regression
    '''
    race = None
    if nihss == 1:
        race = 0
    else:
        race = (nihss + 0.39) / 2.39
    return race


# PLUMBER Study
def p_call_is_mimic():
    # incude TIA
    return (1635 + 191) / 2402


# PLUMBER Study
def p_call_is_hemorrhagic():
    # include ICH and SAH
    return (16 + 85) / 2402


def break_up_ais_patients(p_good_outcome, NIHSS):
    '''
    From pooled meta-analysis in supplement of Saver et al. 2016, we
    break up the good and bad outcome (mRS 0 - 2 and 3 - 5 respectively)
    patients into proportions independent of time to treatment
    However, we consider the proportion of patients that die to be a constant
    regardless of time to treatment
    Probaility of mortality: 0.171361502 
    Probabilities of mRS 0 - 2: 0.205627706, 0.341991342, 0.452380952
    Probabilities of mRS 3 - 5: 0.35678392, 0.432160804, 0.211055276

    '''
    # Assume that probability of death is always constant
    # Stratified by NIHSS, ask Dr. Schwamm to get raw data for a continuous
    # approach
    genpop = 0
    mrs6 = None
    if NIHSS < 7:
        mrs6 = 0.042
    elif NIHSS < 13:
        mrs6 = 0.139
    elif NIHSS < 21:
        mrs6 = 0.316
    else:
        mrs6 = 0.535

    # Good outcomes
    mrs0 = 0.205627706 * p_good_outcome
    mrs1 = 0.341991342 * p_good_outcome
    mrs2 = p_good_outcome - mrs1 - mrs0

    # And bad outcomes
    mrs3 = 0.35678392 * (1 - p_good_outcome - mrs6)
    mrs4 = 0.432160804 * (1 - p_good_outcome - mrs6)
    mrs5 = 0.211055276 * (1 - p_good_outcome - mrs6)

    return [genpop, mrs0, mrs1, mrs2, mrs3, mrs4, mrs5, mrs6]


HAZARDS_MORTALITY = {
    States.GEN_POP: 1,
    States.MRS_0: 1.53,
    States.MRS_1: 1.52,
    States.MRS_2: 2.17,
    States.MRS_3: 3.18,
    States.MRS_4: 4.55,
    States.MRS_5: 6.55
}


def hazard_mort(mrs):
    '''
    Again keep it as a function so that it's easier to do sensitivity analyses
    later on.
    '''
    return HAZARDS_MORTALITY[mrs]


UTILITIES = {
    States.GEN_POP: 1.00,
    States.MRS_0: 1.00,
    States.MRS_1: 0.84,
    States.MRS_2: 0.78,
    States.MRS_3: 0.71,
    States.MRS_4: 0.44,
    States.MRS_5: 0.18
}


def utilities_mrs(mrs):
    return UTILITIES[mrs]


# -----------------------------------
# COSTS
# -----------------------------------


class Costs(object):

    TARGET_YEAR = inflation.Conversion.LAST_YEAR

    # 2014, Dewilde
    DAYS_90_ISCHEMIC = {
        States.GEN_POP: 0,
        States.MRS_0: 6302,
        States.MRS_1: 9448,
        States.MRS_2: 14918,
        States.MRS_3: 26218,
        States.MRS_4: 32502,
        States.MRS_5: 26071
    }

    # 2008, Christensen
    DAYS_90_ICH = {
        States.GEN_POP: 0,
        States.MRS_0: 9500,
        States.MRS_1: 15500,
        States.MRS_2: 18700,
        States.MRS_3: 27400,
        States.MRS_4: 27300,
        States.MRS_5: 27300
    }

    # 2014, Dewilde
    ANNUAL = {
        States.GEN_POP: 0,
        States.MRS_0: 2921,
        States.MRS_1: 3905,
        States.MRS_2: 6501,
        States.MRS_3: 16922,
        States.MRS_4: 42335,
        States.MRS_5: 39723
    }

    # 2008, Christensen
    DEATH = 8100

    # 2014, Sevick
    IVT = 13419

    # 2014, Kleindorfer
    EVT = 6400

    # 2010, Mohr
    TRANSFER = 763

    @staticmethod
    def inflate(TARGET_YEAR):
        for state in Costs.DAYS_90_ISCHEMIC:
            Costs.DAYS_90_ISCHEMIC[state] = (inflation.Conversion.run(
                2014, TARGET_YEAR, Costs.DAYS_90_ISCHEMIC[state]))
        for state in Costs.DAYS_90_ICH:
            Costs.DAYS_90_ICH[state] = (inflation.Conversion.run(
                2008, TARGET_YEAR, Costs.DAYS_90_ICH[state]))
        for state in Costs.ANNUAL:
            Costs.ANNUAL[state] = (inflation.Conversion.run(
                2014, TARGET_YEAR, Costs.ANNUAL[state]))
        Costs.DEATH = inflation.Conversion.run(2008, TARGET_YEAR, Costs.DEATH)
        Costs.IVT = inflation.Conversion.run(2014, TARGET_YEAR, Costs.IVT)
        Costs.EVT = inflation.Conversion.run(2014, TARGET_YEAR, Costs.EVT)
        Costs.TRANSFER = inflation.Conversion.run(2010, TARGET_YEAR,
                                                  Costs.TRANSFER)


def cost_ivt():
    return Costs.IVT


def cost_evt():
    return Costs.EVT


def cost_transfer():
    return Costs.TRANSFER


def first_year_costs(states_hemorrhagic, states_ischemic):

    cost_hemorrhagic = [
        states_hemorrhagic[i] * ((90 / 360) * Costs.DAYS_90_ICH[i] +
                                 ((360 - 90) / 360) * Costs.ANNUAL[i])
        for i in range(States.DEATH)
    ]
    cost_hemorrhagic.append(Costs.DEATH * states_hemorrhagic[States.DEATH])
    cost_ischemic = [
        states_ischemic[i] * ((90 / 360) * Costs.DAYS_90_ISCHEMIC[i] +
                              ((360 - 90) / 360) * Costs.ANNUAL[i])
        for i in range(States.DEATH)
    ]
    cost_ischemic.append(Costs.DEATH * states_ischemic[States.DEATH])
    return sum(cost_hemorrhagic) + sum(cost_ischemic)


def annual_cost(states):
    cost = sum([states[i] * Costs.ANNUAL[i] for i in range(States.DEATH)])
    cost += states[States.DEATH] * Costs.DEATH
    return cost