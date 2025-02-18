import logging

from constants import *

logger = logging.getLogger(__name__)


X = {
    RACE_TYPE_RACING: {
        # $1.16 profit per race     9% of races 447 / 4728      [1.056934, 1.297503],
        # $1.59 profit per race     17% of races 875 / 5108     [0.491663, 1.182646],
        # $0.83 profit per race     5% of races 347 / 7046      [1.049219, 1.402188],
        # $0.67 profit per race     4% of races 360 / 9535      [2.0125, 1.2825],
        # $0.98 profit per race     8% of races 590 / 7541
        BET_TYPE_WIN: [2.086328, 1.148828],
        # $1.52 profit per race     42% of races 1731 / 4108    [0.000033, 1.209581],
        # $1.17 profit per race     31% of races 1357 / 4439    [0.545927, 1.279211],
        # $1.26 profit per race     46% of races 2284 / 4961    [-1.001562, 1.395625],
        # $1.15 profit per race     30% of races 1646 / 5510    [0.526947, 1.321698],
        # $0.97 profit per race     20% of races 1920 / 9535
        BET_TYPE_PLACE: [0.684505, 1.395078],
    },
    RACE_TYPE_GRAYHOUND: {
        # $1.31 profit per race     22% of races 833 / 3752     [1.724365, 1.085333],
        # $0.94 profit per race     11% of races 576 / 5348     [2.003906, 1.184788],
        # $0.84 profit per race     16% of races 1038 / 6533    [1.663013, 1.079235],
        # $0.35 profit per race     4% of races 424 / 10171     [1.825391, 1.184531],
        # $0.15 profit per race     3% of races 390 / 12737
        BET_TYPE_WIN: [1.867187, 1.242969],
        # $1.26 profit per race     21% of races 960 / 4595     [-1.007031, 1.371987],
        # $1.23 profit per race     30% of races 1423 / 4734    [-2.068652, 1.281557],
        # $1.16 profit per race     28% of races 1768 / 6298    [-1.980859, 1.417048],
        # $1.00 profit per race     31% of races 2340 / 7618    [-1.010986, 1.369238],
        # $0.68 profit per race     31% of races 3941 / 12737
        BET_TYPE_PLACE: [0.000092, 1.368193],
    },
    RACE_TYPE_HARNESS: {
        # $0.90 profit per race     11% of races 629 / 5848     [1.348958, 1.151797],
        # $0.72 profit per race     3% of races 187 / 6456      [1.3455, 1.384055],
        # $0.67 profit per race     4% of races 271 / 7541      [1.333431, 1.314992],
        # $1.20 profit per race     8% of races 627 / 7541      [2.186719, 1.148385],
        # $1.08 profit per race     7% of races 549 / 7541
        BET_TYPE_WIN: [1.366349, 1.318551],
        # $0.86 profit per race     48% of races 707 / 1482     [-0.000004, 1.054276],
        # $1.55 profit per race     34% of races 783 / 2290     [0.525, 0.825],
        # $1.89 profit per race     55% of races 1783 / 3235
        BET_TYPE_PLACE: [-1.018457, 1.155212],
    },
}


class NoBetsError(Exception):
    pass


def bet_positive_dutch(runners, bet_chunk, race_type, bet_type):
    """dutch betting on probability"""
    pred = '{}_pred'.format(bet_type)
    pred = '{}_pred'.format(bet_type)
    prob = '{}_prob'.format(bet_type)
    bet = '{}_bet'.format(bet_type)

    x = X[race_type][bet_type]

    # sort runners from favourite to underdog
    runners.sort(key=lambda r: r[pred], reverse=True)

    # start betting on all and cut off worse runner till positive outcome
    for num_bets in range(len(runners), 0, -1):

        # reset bets
        for runner in runners:
            runner[bet] = 0

        # recreate smaller pool
        pool = runners[:num_bets]
        # print('pool is {} from {} bets'.format(len(pool), num_bets))

        # all prediction values
        total_preds = sum([r[pred] for r in pool])

        # dutch for all in pool
        profits = []
        scales = []
        for runner in pool:
            # scale bet according to prediction
            runner[bet] = bet_chunk * runner[pred] / total_preds
            runner['{}_type'.format(bet)] = 'parimutuel'

            # need to check all as we scale to probs and not odds
            if bet_type == 'W':
                odds = runner['win_odds']
                scaled = runner['win_scaled']
            elif bet_type == 'P':
                odds = runner['place_odds']
                scaled = runner['place_scaled']
            profits.append(runner[bet] * odds - bet_chunk)
            scales.append(runner[prob] / scaled)

        ###################################################################################
        # MIN PROFIT
        ###################################################################################
        min_profit_flag = False
        min_profit = min(profits)
        if min_profit > bet_chunk * x[0]:
            min_profit_flag = True

        ###################################################################################
        # MIN SCALED
        ###################################################################################
        min_scaled_flag = False
        min_scaled = min(scales)
        if min_scaled >= x[1]:
            min_scaled_flag = True

        if min_profit_flag and min_scaled_flag:
            # print('breaking: {} {} {} {}'.format(min_profit_flag, avg_profit_flag, num_bets_flag, min_probs2scale_flag))
            break

    else:
        # reset going back
        for r in runners:
            r[bet] = 0
        return runners, 0

    # put bets from pool into runners
    for p in pool:
        for r in runners:
            if r['runnerNumber'] == p['runnerNumber']:
                r[bet] = p[bet]
                r['{}_type'.format(bet)] = p['{}_type'.format(bet)]
                break

    return runners, num_bets
