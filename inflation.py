'''
http://www.usinflationcalculator.com/
CPI data provided by US Bureau of Labor Statistics
'''


class Conversion(object):
    CPI = [
        9.9, 10, 10.1, 10.9, 12.8, 15.1, 17.3, 20, 17.9, 16.8, 17.1, 17.1,
        17.5, 17.7, 17.4, 17.1, 17.1, 16.7, 15.2, 13.7, 13, 13.4, 13.7, 13.9,
        14.4, 14.1, 13.9, 14, 14.7, 16.3, 17.3, 17.6, 18, 19.5, 22.3, 24.1,
        23.8, 24.1, 26, 26.5, 26.7, 26.9, 26.8, 27.2, 28.1, 28.9, 29.1, 29.6,
        29.9, 30.2, 30.6, 31, 31.5, 32.4, 33.4, 34.8, 36.7, 38.8, 40.5, 41.8,
        44.4, 49.3, 53.8, 56.9, 60.6, 65.2, 72.6, 82.4, 90.9, 96.5, 99.6,
        103.9, 107.6, 109.6, 113.6, 118.3, 124, 130.7, 136.2, 140.3, 144.5,
        148.2, 152.4, 156.9, 160.5, 163, 166.6, 172.2, 177.1, 179.9, 184,
        188.9, 195.3, 201.6, 207.3, 215.303, 214.537, 218.056, 224.939,
        229.594, 232.957, 236.736, 237.017, 240.007
    ]
    FIRST_YEAR = 1913
    LAST_YEAR = 2016

    @staticmethod
    def run(original_year, updated_year, cost):
        '''
        Earliest date: 1913. Current last date is 2016. No bounds
        checking so please be careful
        '''
        i_orig = original_year - Conversion.FIRST_YEAR
        i_update = updated_year - Conversion.FIRST_YEAR
        return cost * (Conversion.CPI[i_update] / Conversion.CPI[i_orig])