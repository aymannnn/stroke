import enum
import constants
import numpy as np


def p_lvo_logistic_helper(b0, b1, race):
    return (1.0 / (1.0 + np.exp(-b0 - b1 * race)))


def p_lvo_given_ais(race, add_uncertanity):
    # Perez de la Ossa et al. Stroke 2014 data for p lvo given ais
    # See random python scripts notebook for derivation
    p_lvo = p_lvo_logistic_helper(-2.9297, 0.5533, race)

    if add_uncertanity is True:
        lower = p_lvo_logistic_helper(-3.6526, 0.4141, race)
        upper = p_lvo_logistic_helper(-2.2067, 0.6925, race)
        p_lvo = np.random.uniform(lower, upper)

    return p_lvo


def p_good_outcome_post_evt_success(time_onset_reperfusion, NIHSS):
    '''
    Saver et al. JAMA 2016, Schlemm analysis
    Note: had to redo the regression
    '''
    beta = (-0.00879544 - 9.01419716e-05 * time_onset_reperfusion)
    return np.exp(beta * NIHSS)


def p_good_outcome_no_reperfusion(NIHSS):
    # Schlemm, used a few different sources for points on the piecewise
    # linear regression (3 distinct points: 0.05 at NIHSS 20, 1 at NIHSS 0,
    # and 0.3 at for an NIHSS at 16)
    if NIHSS >= 20:
        return 0.05
    else:
        return (-0.0464 * NIHSS) + 1.0071


def p_good_outcome_ais_no_lvo_got_tpa(time_onset_tpa, NIHSS):
    '''
    * Note that if your time from onset to tPA is > 270, you won't actually
    * get tPA.
    Schelmm analysis, extracted from a few sources and assumed that
    there is interaction between treatment effect of thrombolysis and
    stroke severity
    Didn't have data for odds ratio with time for patients without LVO,
    but there is no consistent evidence that it differs for patients
    with and without LVO
    '''
    baseline_prob = 0.001 * NIHSS**2 - 0.0615 * NIHSS + 1
    if time_onset_tpa > constants.time_limit_tpa():
        return baseline_prob
    else:
        odds_ratio = -0.0031 * time_onset_tpa + 2.068
        baseline_prob_to_odds = baseline_prob / (1 - baseline_prob)
        new_odds = baseline_prob_to_odds * odds_ratio
        adjusted_prob = new_odds / (1 + new_odds)
        return adjusted_prob


def p_reperfusion_endovascular():
    # Saver et al. JAMA 2016, Schlemm analysis
    return 0.71


def p_early_reperfusion_thrombolysis(time_to_groin):
    return 0.18 * min([70, time_to_groin]) / 70


class IschemicModel(object):
    def __init__(self, arguments, add_lvo_uncertainty):

        self.sex = arguments['sex']
        self.age = arguments['age']
        self.RACE = arguments['RACE']
        self.NIHSS = constants.race_to_nihss(self.RACE)

        self.onset_needle_primary = (
            arguments['time_since_symptoms'] + arguments['time_to_primary'] +
            constants.Times.door_needle_primary)

        self.onset_needle_comprehensive = (
            arguments['time_since_symptoms'] +
            arguments['time_to_comprehensive'] +
            constants.Times.door_needle_comprehensive)

        self.onset_evt_noship = (arguments['time_since_symptoms'] +
                                 arguments['time_to_comprehensive'] +
                                 constants.Times.door_to_intra_arterial)

        self.onset_evt_ship = (
            arguments['time_since_symptoms'] + arguments['time_to_primary'] +
            constants.Times.door_needle_primary + arguments['transfer_time'] +
            constants.Times.transfer_to_intra_arterial)

        self.p_lvo = p_lvo_given_ais(self.RACE, add_lvo_uncertainty)
        # if add_lvo_uncertainty:
        #   print(self.p_lvo) # dummy debug

        self.model_is_necessary = self.is_there_an_option()
        if self.model_is_necessary is False:
            self.cutoff_location = constants.no_tx_where_to_go(self.RACE)

    def is_there_an_option(self):
        '''
        So the problem is what if you can't get treatment at either center?
        In this scenario, we define a RACE cutoff at which to take the patient
        to the comprehensive; if they don't make the cutoff, don't bother.
        This happens when:
        1) onset to needle primary is too long and
        2) onset to EVT at the comprehensive is too long and
        '''
        option_exists = True
        if ((self.onset_needle_primary > constants.time_limit_tpa())
                and (self.onset_evt_noship > constants.time_limit_evt())):
            option_exists = False

        return option_exists

    def get_ais_outcomes(self, key):
        outcomes = None
        if key == "Primary":
            outcomes = self.run_primary_center()
        elif key == "Comprehensive":
            outcomes = self.run_comprehensive_center()
        elif key == "Drip and Ship":
            outcomes = self.run_primary_then_ship()
        return outcomes

    def run_primary_center(self):
        '''
        Returns the probability of a good outcome, the proportion that got EVT,
        and the proportion that got TPA by going straight to the
        primary center
        return {'p_good': p_good, 'p_tpa': p_tpa, 'p_evt': p_evt} 
        '''
        p_good = self.get_p_good(self.onset_needle_primary)
        p_tpa = 1
        p_evt = 0
        p_transfer = 0

        return {
            'p_good': p_good,
            'p_tpa': p_tpa,
            'p_evt': p_evt,
            'p_transfer': p_transfer
        }

    def run_comprehensive_center(self):
        '''
        Returns the probability of a good outcome, the proportion that got EVT,
        and the proportion that got TPA  by going straight to the
        comprehensive
        return {'p_good': p_good, 'p_tpa': p_tpa, 'p_evt': p_evt} 
        '''
        p_transfer = 0
        p_tpa = 0
        p_evt = self.p_lvo
        if self.onset_needle_comprehensive < constants.time_limit_tpa():
            p_tpa = 1
        p_good = self.get_p_good(self.onset_needle_comprehensive,
                                 self.onset_evt_noship)
        return {
            'p_good': p_good,
            'p_tpa': p_tpa,
            'p_evt': p_evt,
            'p_transfer': p_transfer
        }

    def run_primary_then_ship(self):
        '''
        Note -> this method will return FALSE if you cannot ship to the
        comprehensive center in time to get EVT. OTherwise, it will return,
        just like the other two strategies, the probability of a good outcome,
        the proportion that got EVT, and the proportion that got TPA 
        by going straight to the primary center then transfering
        to the comprehnsive
        return {'p_good': p_good, 'p_tpa': p_tpa, 'p_evt': p_evt} 
        '''
        # However, this is not an option if the time from onset to EVT by
        # shipping is greater than the time limit to EVT
        p_good = 0
        p_tpa = 0
        p_evt = 0
        p_transfer = 1
        if self.onset_evt_ship > constants.time_limit_evt():
            return False
        else:
            p_tpa = 1
            p_evt = self.p_lvo
            p_good = self.get_p_good(self.onset_needle_primary,
                                     self.onset_evt_ship)
            return {
                'p_good': p_good,
                'p_tpa': p_tpa,
                'p_evt': p_evt,
                'p_transfer': p_transfer
            }

    def get_p_good(self, onset_to_tpa, onset_to_evt=None):

        p_good = 0

        # Note that this will take into account if the time from onset to tPA
        # is too high
        baseline_p_good = p_good_outcome_ais_no_lvo_got_tpa(
            onset_to_tpa, self.NIHSS)

        # For the non-LVO patients, your probability of a good outcome
        # is only effected by the time that you got tPA
        p_good += ((1 - self.p_lvo) * baseline_p_good)

        # Now, to calculate the probability of a good outcome for
        # somebody with an LVO, we need to calculate the probability
        # of reperfusion

        # TODO -> probability of early reperfusion by needle-to-groin

        p_reperfused = 0
        p_not_reperfued = self.p_lvo

        if onset_to_evt:
            # Reperfused by EVT
            p_reperfused = (self.p_lvo * p_reperfusion_endovascular())
            p_not_reperfued -= p_reperfused

        p_good += p_not_reperfued * baseline_p_good

        if onset_to_evt:
            p_good_post_evt = p_good_outcome_post_evt_success(
                onset_to_evt, self.NIHSS)
            higher_p_good = p_good_post_evt
            if higher_p_good < baseline_p_good:
                higher_p_good = baseline_p_good
            p_good += p_reperfused * higher_p_good
            # TODO -> sometimes the post EVT and baseline p good are really
            # close, mainly for patients getting EVT at the end and tPA at the
            # start and for patients with low NIHSS scores
            '''
            if p_good_post_evt < baseline_p_good:
                print('Post EVT is WORSE than baseline p good? What?',
                      p_good_post_evt, baseline_p_good, self.NIHSS, self.RACE,
                      onset_to_tpa, onset_to_evt)
            '''
        return p_good
