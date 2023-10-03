#!/usr/bin/env python3
"""
This is a module to compute fantasy football statistics
"""
__author__ = "Jacob Elias"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import os
from prettytable import PrettyTable
from espn_api.football import League
import datetime
import time
import logging
import pdfkit
import json


Weeks = {
    # Wednesday - Wednesday - Sunday
    "1": ["2023-08-30", "2023-09-06", "2023-09-03"],
    "2": ["2023-09-06", "2023-09-13", "2023-09-10"],
    "3": ["2023-09-13", "2023-09-20", "2023-09-17"],
    "4": ["2023-09-20", "2023-09-27", "2023-09-24"],
    "5": ["2023-09-27", "2023-10-04", "2023-10-01"],
    "6": ["2023-10-04", "2023-10-11", "2023-10-08"],
    "7": ["2023-10-11", "2023-10-18", "2023-10-15"],
    "8": ["2023-10-18", "2023-10-25", "2023-10-22"],
    "9": ["2023-10-25", "2023-11-01", "2023-10-29"],
    "10": ["2023-11-01", "2023-11-08", "2023-11-05"],
    "11": ["2023-11-08", "2023-11-15", "2023-11-12"],
    "12": ["2023-11-15", "2023-11-22", "2023-11-19"],
    "13": ["2023-11-22", "2023-11-29", "2023-11-26"],
    "14": ["2023-11-29", "2023-12-06", "2023-12-03"],
    "15": ["2023-12-06", "2023-12-13", "2023-12-10"],
    "16": ["2023-12-13", "2023-12-20", "2023-12-17"],
    "17": ["2023-12-20", "2023-12-27", "2023-12-24"],
    "18": ["2023-12-28", "2024-01-03", "2023-12-31"],
}


POSITIONS = ["QB", "WR", "TE", "RB"]


def PrettyFloat(num):
    return "%0.2f" % num


def DateStringToDateTime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def TradeGetWeek(trade):
    trade_time_stamp = datetime.datetime.fromtimestamp(trade.date/1000.0)
    print("Trade Date: ", trade.date, " Timestamped: ", trade_time_stamp)
    for week, dates in Weeks.items():
        if DateStringToDateTime(dates[0]) < trade_time_stamp < DateStringToDateTime(dates[1]):
            return week


def TradeGetWeekBySunday(trade):
    trade_time_stamp = datetime.datetime.fromtimestamp(trade.date/1000.0)
    last_sunday = DateStringToDateTime(Weeks["1"][2])
    print("Trade Date: ", trade.date, " Timestamped: ", trade_time_stamp)
    for week, dates in Weeks.items():
        if last_sunday < trade_time_stamp < DateStringToDateTime(dates[2]):
            return str(int(week) - 1)
        last_sunday = DateStringToDateTime(dates[2])


def TradeGetTeams(activity):
    team1 = activity.actions[0][0]
    for idx in activity.actions:
        if team1.team_id is not idx[0].team_id:
            return team1, idx[0]
    print("ERROR Calculating Trade TEAMS!! Trade Activity: ", activity)
    return None


# Given a trade and a team, return the players traded away
def TradeGetPlayers(trade, team):
    players = []
    for event in trade.actions:
        if event[0].team_id == team.team_id:
            players.append(event[2])
            print("[Debug] " + team.team_name, " Sent ", event[2].name)
    return players


def playerAbbreviation(player_name):
    split = player_name.split(" ")
    return split[0][0] + ". " + split[1]


def GetTradeDate(trade):
    s = trade.date / 1000.0
    return datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d')
#     return datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d')
# '2009-03-08'


def GetTradeActivities(league):
    tradeActivities = []
    for activity in league.recent_activity(50, "TRADED"):
        tradeActivities.append(activity)
    return tradeActivities


def biggestBlowOut(league, week):
    outcomes = []

    box_scores = league.box_scores(week)

    for matchup in box_scores:
        diff = 0
        if not isinstance(matchup.home_team, int) and not isinstance(matchup.away_team, int):
            # print("[Debug][biggestBlowout] Matchup home team: ", matchup.home_team.team_name)
            # print("[Debug][biggestBlowout] Matchup away team: ", matchup.away_team.team_name)
            if matchup.home_score >= matchup.away_score:
                diff = matchup.home_score - matchup.away_score
                outcomes.append((matchup, diff))
            else:
                diff = matchup.away_score - matchup.home_score
                outcomes.append((matchup, diff))

    biggest_blowout, diff = sorted(
        outcomes, key=lambda tup: tup[1], reverse=True)[0]

    j = PrettyTable()
    title = "Beat that Ass Blowout".format(diff)
    j.title = title
    j.field_names = [biggest_blowout.home_team.team_name,
                     biggest_blowout.away_team.team_name]
    j.add_row([biggest_blowout.home_score, biggest_blowout.away_score])
    j.align = "c"
    print(j)

    ret = {
        "team1": biggest_blowout.home_team.team_name,
        "team2": biggest_blowout.away_team.team_name,
        "score1": biggest_blowout.home_score,
        "score2": biggest_blowout.away_score
    }

    return ret


def closestGame(league, week):
    outcomes = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        # For Each Matchip calculate the diff
        diff = 0
        if matchup.home_score >= matchup.away_score:
            diff = matchup.home_score - matchup.away_score
            outcomes.append((matchup, diff))
        else:
            diff = matchup.away_score - matchup.home_score
            outcomes.append((matchup, diff))

    biggest_blowout, diff = sorted(
        outcomes, key=lambda tup: tup[1], reverse=False)[0]

    j = PrettyTable()
#     title = "Biggest Blowout ({0})".format(diff)
    title = "Nail Biter of the Week".format(diff)
    j.title = title
    j.field_names = [biggest_blowout.home_team.team_name,
                     biggest_blowout.away_team.team_name]
    j.add_row([biggest_blowout.home_score, biggest_blowout.away_score])
    j.align = "c"
    print(j)

    ret = {
        "team1": biggest_blowout.home_team.team_name,
        "team2": biggest_blowout.away_team.team_name,
        "score1": biggest_blowout.home_score,
        "score2": biggest_blowout.away_score
    }

    return ret


def biggestBenchWarmer(league, week, position):
    if position not in POSITIONS:
        return []

    benchWarmers = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        # For Each Matchip calculate the diff
        for player in matchup.home_lineup:
            if player.position == position and player.slot_position == "BE":
                benchWarmers.append(
                    (player.points, player.name, player.position, matchup.home_team.team_name))

        for player in matchup.away_lineup:
            if player.position == position and player.slot_position == "BE":
                benchWarmers.append(
                    (player.points, player.name, player.position, matchup.away_team.team_name))

    return sorted(benchWarmers, key=lambda tup: tup[0], reverse=True)


def topPlayers(league, week):

    topPlayers = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        # For Each Matchip calculate the diff
        for player in matchup.home_lineup:
            if player.slot_position != "BE":
                topPlayers.append(
                    (player.points, player.name, player.position, matchup.home_team.team_name))

        for player in matchup.away_lineup:
            if player.slot_position != "BE":
                topPlayers.append(
                    (player.points, player.name, player.position, matchup.away_team.team_name))

    return sorted(topPlayers, key=lambda tup: tup[0], reverse=True)


def prettyPrintBenchWarmers(benchWarmers):
    benchWarmersOut = []
    x = PrettyTable()
    x.field_names = ["Points", "Player", "Team"]
    x.title = 'Biggest Benchwarmers'
    for _, warmer in enumerate(benchWarmers):
        x.add_row([warmer[0], warmer[1], warmer[3]])
        benchWarmersOut.append([warmer[0], warmer[1], warmer[3]])
    print(x)
    print("  ")
    return benchWarmersOut


def prettyPrintTopScorers(benchWarmers):
    topScorers = []
    x = PrettyTable()
    x.field_names = ["Points", "Player", "Team"]
    x.title = "Top Scorers"
    for _, warmer in enumerate(benchWarmers):
        x.add_row([warmer[0], warmer[1], warmer[3]])
        topScorers.append([warmer[0], warmer[1], warmer[3]])
    print(x)
    print("  ")
    return topScorers

# ### Total Points Played / Best Possible Points


def optimalLineup(lineup):

    QB = 2
    RB = 2
    WR_TE = 3
    FLEX = 1

    starters = []
    starter_ouput = 0
    all_players = []

    optimal_players = []
    optimal_output = 0

    for player in lineup:
        if player.slot_position != "IR" and player.slot_position != "BE":
            starters.append(player)
            starter_ouput += player.points

    all_players = sorted(lineup, key=lambda x: x.points, reverse=True)

    # Get Best 2QBs
    for player in all_players:
        if QB > 0 and player.position == "QB":
            QB = QB - 1
            optimal_players.append(player)
            optimal_output += player.points

    # Get Single FLEX Score
    for player in all_players:
        if FLEX > 0 and (player.position == "RB" or player.position == "WR" or player.position == "TE") and (player not in optimal_players):
            FLEX = FLEX - 1
            optimal_players.append(player)
            optimal_output += player.points

    # Get Best 2 RBs
    for player in all_players:
        if RB > 0 and (player.position == "RB") and (player not in optimal_players):
            RB = RB - 1
            optimal_players.append(player)
            optimal_output += player.points

    # Get Best WR/TE
    for player in all_players:
        if WR_TE > 0 and (player.position == "TE" or player.position == "WR") and (player not in optimal_players):
            WR_TE = WR_TE - 1
            optimal_players.append(player)
            optimal_output += player.points

    return starter_ouput, optimal_output


def manager_effiency(league, week):
    manager_eff = []
    for matchup in league.box_scores(week):

        if not isinstance(matchup.home_team, int):
            starter_ouput, optimal_output = optimalLineup(matchup.home_lineup)
            manager_eff.append((matchup.home_team.team_name, starter_ouput,
                               optimal_output, starter_ouput/optimal_output))
        if not isinstance(matchup.away_team, int):
            starter_ouput, optimal_output = optimalLineup(matchup.away_lineup)
            manager_eff.append((matchup.away_team.team_name, starter_ouput,
                               optimal_output, starter_ouput/optimal_output))
            manager_eff = sorted(
                manager_eff, key=lambda manager_eff: manager_eff[3], reverse=True)
    return manager_eff


def prettyPrintManagerEff(manager_eff):

    x = PrettyTable()
    x.title = ' Galaxy Brain Manager'
    x.field_names = ["Team", "Output/Optimal", "% Accuracy"]

    galaxyManager = {}
    mikeZimmerManager = {}

    manager_eff_sorted = sorted(
        manager_eff, key=lambda manager_eff: manager_eff[3], reverse=True)
    for manager in manager_eff_sorted[:1]:
        fraction = "{0:.0f}/{1:.0f}".format(manager[1], manager[2])
        percentage = "{0:.0f}".format(manager[3] * 100)
        x.add_row([manager[0], fraction, percentage])
        # galaxyManager["msg"] = manager[0] + " " + fraction + " " + percentage
        galaxyManager = {
            "r1c1": "Team",
            "r1c2": "Output/Optimal",
            "r1c3": "% Accuracy",
            "r2c1": manager[0],
            "r2c2": fraction,
            "r2c3": percentage,
        }
    print(x)

    y = PrettyTable()
    y.title = 'Mike Zimmer Manager of the Week'
    y.field_names = ["Team", "Output/Optimal", "% Accuracy"]

    worst_manager_eff_sorted = sorted(
        manager_eff, key=lambda manager_eff: manager_eff[3], reverse=False)
    for manager in worst_manager_eff_sorted[:1]:
        fraction = "{0:.0f}/{1:.0f}".format(manager[1], manager[2])
        percentage = "{0:.0f}".format(manager[3] * 100)
        y.add_row([manager[0], fraction, percentage])
        # mikeZimmerManager["msg"] = manager[0] + \
        # " " + fraction + " " + percentage
        mikeZimmerManager = {
            "r1c1": "Team",
            "r1c2": "Output/Optimal",
            "r1c3": "% Accuracy",
            "r2c1": manager[0],
            "r2c2": fraction,
            "r2c3": percentage,
        }

    print(y)

    return (galaxyManager, mikeZimmerManager)


# Season Long Mananger Effenciey returns -> sorted list(team_name, total_output, optimal_output, accuracy %)


def seasonEffiency(league, week):
    weekly_eff = {}
    output_eff = []
    # For Each Week Gather the Effenciey
    for i in range(1, week+1):
        #         print("Week: ", i)
        weekly_eff[i] = {}
        for matchup in league.box_scores(i):

            if not isinstance(matchup.home_team, int):
                starter_ouput, optimal_output = optimalLineup(
                    matchup.home_lineup)
                weekly_eff[i][matchup.home_team.team_name] = [
                    starter_ouput, optimal_output, starter_ouput/optimal_output]

            if not isinstance(matchup.away_team, int):
                starter_ouput, optimal_output = optimalLineup(
                    matchup.away_lineup)
                weekly_eff[i][matchup.away_team.team_name] = [
                    starter_ouput, optimal_output, starter_ouput/optimal_output]
#           manager_eff.append((matchup.away_team.team_name,starter_ouput,optimal_output, starter_ouput/optimal_output))

    # For each week for each team
    for team in league.teams:
        output = 0
        optimal = 0
        accuracy = []
        for i in range(1, week+1):
            #             print(team.team_name, " ", weekly_eff[i][team.team_name])
            output += weekly_eff[i][team.team_name][0]
            optimal += weekly_eff[i][team.team_name][1]
            accuracy.append(weekly_eff[i][team.team_name][2])

        output_eff.append((team.team_name, output, optimal,
                          sum(accuracy)/len(accuracy)))

    output_eff = sorted(
        output_eff, key=lambda output_eff: output_eff[3], reverse=True)
    return output_eff


def prettyPrintSeasonEff(total_season_eff):

    y = PrettyTable()
    y.title = "Total Manager Efficiency Rankings"
    y.field_names = ["Team", "Output/Optimal", "%"]
    for team in total_season_eff:
        fraction = "{0:.0f}/{1:.0f}".format(team[1], team[2])
        percentage = "{0:.0f}".format(team[3] * 100)
        y.add_row([team[0], fraction, percentage])
    print(y)


def worstWin(league, week):
    box_scores = league.box_scores(week)
    lowestWinningScore = 99999999999
    saved = None
    for matchup in box_scores:
        if matchup.home_score >= matchup.away_score:
            lowestWinningScore = min(matchup.home_score, lowestWinningScore)
        else:
            lowestWinningScore = min(matchup.away_score, lowestWinningScore)

        if lowestWinningScore == matchup.away_score or lowestWinningScore == matchup.home_score:
            saved = matchup

    j = PrettyTable()
    j.title = "Garbage Win (Lowest Winning Score)"
    j.field_names = [saved.home_team.team_name, saved.away_team.team_name]
    j.add_row([saved.home_score, saved.away_score])
    j.align = "c"
    print(j)

    ret = {
        "team1": saved.home_team.team_name,
        "team2": saved.away_team.team_name,
        "score1": saved.home_score,
        "score2": saved.away_score
    }

    return ret


def worstLoss(league, week):
    box_scores = league.box_scores(week)
    higestLoss = 0
    saved = None
    for matchup in box_scores:
        if matchup.home_score >= matchup.away_score:
            higestLoss = max(matchup.away_score, higestLoss)
        else:
            higestLoss = max(matchup.home_score, higestLoss)

        if higestLoss == matchup.away_score or higestLoss == matchup.home_score:
            saved = matchup

    j = PrettyTable()
    j.title = "Good Effort Kid (Highest Scoring Loser)"
    j.field_names = [saved.home_team.team_name, saved.away_team.team_name]
    j.add_row([saved.home_score, saved.away_score])
    j.align = "c"
    print(j)

    ret = {
        "team1": saved.home_team.team_name,
        "team2": saved.away_team.team_name,
        "score1": saved.home_score,
        "score2": saved.away_score
    }

    return ret


def startingLineupAverage(lineup):
    starterOutput = []
    for player in lineup:
        if player.slot_position != "BE" and player.slot_position != "IR":
            starterOutput.append(player.points)
    if starterOutput == 0 or len(starterOutput) == 0:
        return -1
    return sum(starterOutput)/len(starterOutput)


def highestScoringStarter(lineup):
    highestScore = 0
    bestPlayer = None
    for player in lineup:
        if player.slot_position != "BE" and player.slot_position != "IR":
            if player.points > highestScore:
                highestScore = player.points
                bestPlayer = player
    return bestPlayer


# Team with greatest differences between max player and team average
def topHeavyTeams(league, week):
    allTeams = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:

        # HOME TEAM
        if not isinstance(matchup.home_team, int):
            avg = startingLineupAverage(matchup.home_lineup)
            maxPlayer = highestScoringStarter(matchup.home_lineup)
            allTeams.append((matchup.home_team.team_name, avg,
                            maxPlayer, maxPlayer.points - avg))

        # AWAY TEAM
        if not isinstance(matchup.away_team, int):
            avg = startingLineupAverage(matchup.away_lineup)
            maxPlayer = highestScoringStarter(matchup.away_lineup)
            allTeams.append((matchup.away_team.team_name, avg,
                            maxPlayer, maxPlayer.points - avg))

    allTeamSorted = sorted(allTeams, key=lambda tup: tup[3], reverse=True)
    return allTeamSorted


def prettyPrintTopHeavy(topHeavyList):

    j = PrettyTable()
    j.title = "One Player Wonder"
    j.field_names = ["Team", "Top Player Pts", "Team Avg", "Diff"]
    for index, team in enumerate(topHeavyList[:1]):
        x = "{0}: {1}".format(team[2].name, team[2].points)
        j.add_row([team[0], x, "{:.2f}".format(team[1]),
                  "{:.2f}".format((team[2].points - team[1]))])
    print(j)

    topHeavyList = {
        "r1c1": "Team",
        "r1c2": "Top Player Points",
        "r1c3": "Team Avg",
        "r2c1": team[0],
        "r2c2": x,
        "r2c3": "{:.2f}".format(team[1]),
    }

    return topHeavyList


# Team with greatest differences between max player and team average
def highestTeamAverageForStarters(league, week):
    allTeams = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:

        # HOME TEAM
        if not isinstance(matchup.home_team, int):
            avg = startingLineupAverage(matchup.home_lineup)
            allTeams.append((matchup.home_team.team_name, avg))

        # AWAY TEAM
        if not isinstance(matchup.away_team, int):
            avg = startingLineupAverage(matchup.away_lineup)
            # maxPlayer = highestScoringStarter(matchup.away_lineup)
            allTeams.append((matchup.away_team.team_name, avg))

    allTeamSorted = sorted(allTeams, key=lambda tup: tup[1], reverse=True)
    return allTeamSorted


def prettyPrintHitters(hitters):

    ret = {}
    j = PrettyTable()
    j.title = "Whole Team Getting Buckets"
    j.field_names = ["Team", "Avg Points Per Player"]

    for team in hitters[:1]:
        j.add_row([team[0], "{:.2f}".format(team[1])])

        ret = {
            "team1": "Team",
            "team2": "Avg Points Per Player",
            "score1": team[0],
            "score2": "{:.2f}".format(team[1]),
        }

    print(j)
    return ret


def standings(league, week):

    standingsJson = []

    j = PrettyTable()
    x = "JCPY FFL Week {0} Power Rankings".format(league.current_week)
    print(x)
    j.title = x

    # Use current week - 1, so we don't calculate empty scores
    total_season_eff = seasonEffiency(league, league.current_week-1)

    j.field_names = ["Ranking", "Team", "Record", " Yoff %",
                     " Lineup IQ", "PF/PA", "# Moves", "$ Left", "Divison"]

    for index, tup in enumerate(league.power_rankings()):
        team = tup[1]

        record = "{0}-{1}-{2} {3}{4}".format(
            team.wins, team.losses, team.ties, team.streak_type[0], team.streak_length)

        # Find Team IQ
        for i in total_season_eff:
            if i[0] == team.team_name:

                yoff_pct = "{0:.0f}%".format(team.playoff_pct)
                manager_iq = "{0:.0f}/{1:.0f}: {2:.0f}%".format(
                    i[1], i[2], i[3]*100)
                pf_pa = "{0:.0f}/{1:.0f}".format(team.points_for,
                                                 team.points_against)
                moves_made = team.acquisitions + team.drops + team.trades
                money_left = 100 - team.acquisition_budget_spent
                row = [index+1, team.team_name, record, yoff_pct, manager_iq,
                       pf_pa, moves_made, money_left, team.division_name]
                j.add_row(row)
                standingsJson.append(row)

    print(j)
    return standingsJson


def divison_strength(league, week):

    j = PrettyTable()
#     x = "JCPY FFL Week {0} Power Rankings".format(week)
#     j.title = x
#     j.field_names=["Ranking", "Team", "Record", " Yoff Percentage"]
    rankings = []
    east_rankings = []
    west_rankings = []
    for index, tup in enumerate(league.power_rankings()):

        team = tup[1]
        ranking = float(tup[0])
        rankings.append(ranking)

        if team.division_name == "East":
            east_rankings.append(ranking)
        else:
            west_rankings.append(ranking)

    east_strength = sum(east_rankings)
    west_strength = sum(west_rankings)

    strong_division = ""
    if east_strength > west_strength:
        strong_division = "East"
        pct_stronger = (1 - (west_strength / east_strength)) * 100
        x = "East Division is {0:.2f%} stronger than West".format(pct_stronger)
    else:
        strong_division = "West"
        pct_stronger = (1 - (east_strength / west_strength)) * 100
        x = "West Division is {0:.2f}% stronger than East".format(pct_stronger)

    print(x)
    return x


def getOpponentsScores(league):

    teams = {}
    for team in league.teams:
        opposing_scores = []
        for w in range(1, league.current_week):
            box_scores = league.box_scores(w)
            for matchup in box_scores:
                if matchup.home_team == team:
                    opposing_scores.append(matchup.away_score)
                elif matchup.away_team == team:
                    opposing_scores.append(matchup.home_score)

        teams[team.team_name] = opposing_scores
    return teams


def scheduleSwap(league):

    big_d = {}
    opposing_points_dict = getOpponentsScores(league)
#     print(opposing_points_dict)
    for home_team in league.teams:
        big_d[home_team.team_name] = {}
        my_points = home_team.scores

        for away_team in league.teams:
            #             if home_team == away_team:
            #                 big_d[home_team.team_name][away_team.team_name] = (-1,-1,-1)
            #                 continue

            op_sched = opposing_points_dict[away_team.team_name]
#             print("Away_team: " ,away_team.team_name, " ",op_sched )
#             print("Home_team: ", home_team.team_name, " ", my_points)
            wins, losses, ties = 0, 0, 0
            for idx in range(len(op_sched)):
                if my_points[idx] > op_sched[idx]:
                    wins += 1
                elif op_sched[idx] > my_points[idx]:
                    losses += 1
                # If the opposing schedule played me?
                elif op_sched[idx] == my_points[idx]:
                    ties += 1

            big_d[home_team.team_name][away_team.team_name] = (
                wins, losses, ties)

    return big_d


def main(swid, espn_s2, league_id, week):
    """ Main entry point of the app """
    league = League(league_id=league_id, year=2023, espn_s2=espn_s2, swid=swid)

    ############# Final Output #################################

    weeksOutput = {"weeks": []}
    current_week = league.current_week
    for week in range(1, current_week):
        jsonWeek = {}
        print("week: ", week)
        # Worst Win
        worstWinDict = worstWin(league, week)

        jsonWeek["garbageWin"] = worstWinDict
        # Worst Loss
        worstLossDict = worstLoss(league, week)
        jsonWeek["goodEffortKid"] = worstLossDict

        # Biggest Blowout
        biggestBlowoutDict = biggestBlowOut(league, week)
        jsonWeek["biggestBlowout"] = biggestBlowoutDict

        # Closest Game
        closestGameDict = closestGame(league, week)
        jsonWeek["nailBiter"] = closestGameDict

        # Best and Worst Manager
        manager_eff = manager_effiency(league, week)
        galaxy, mike = prettyPrintManagerEff(manager_eff)
        jsonWeek["galaxyManger"] = galaxy
        jsonWeek["mikeZimmer"] = mike

        # Top Heavy
        topHeavyList = topHeavyTeams(league, week)
        topHeavyDict = prettyPrintTopHeavy(topHeavyList)
        jsonWeek['onePlayer'] = topHeavyDict

        # Everyone was hitting
        hitters = highestTeamAverageForStarters(league, week)
        wholeTeamDict = prettyPrintHitters(hitters)
        jsonWeek['wholeTeam'] = wholeTeamDict

        qbWarmers = biggestBenchWarmer(league, week, "QB")
        rbWarmers = biggestBenchWarmer(league, week, "RB")
        teWarmers = biggestBenchWarmer(league, week, "TE")
        wrWarmers = biggestBenchWarmer(league, week, "WR")

        allWarmers = qbWarmers + rbWarmers + teWarmers + wrWarmers
        allWarmers = sorted(allWarmers, key=lambda tup: tup[0], reverse=True)
        # print("All Warmers: ", allWarmers)
        benchWarmers = prettyPrintBenchWarmers(allWarmers[:5])
        jsonWeek["benchWarmers"] = benchWarmers
        topScorers = prettyPrintTopScorers(topPlayers(league, week)[:5])
        jsonWeek["topScorers"] = topScorers

        weeksOutput["weeks"].append(jsonWeek)
        print("Printing JSON Week")
        weeksStr = json.dumps(weeksOutput)
        print(weeksStr)
        print("Printed JSON Week")

    # print(weeks)

    standingJson = standings(league, week)
    weeksOutput["standings"] = standingJson
    weeksStr = json.dumps(weeksOutput)
    print(weeksStr)
    print("Printed JSON Week")
    divison_strength(league, week)

    table = PrettyTable()
    table.title = "Schedule Swap"
    table.hrules = True
    team_name_header = [" "]
    for i in range(len(league.teams)):
        team_name_header.append(league.teams[i].team_name)
    # print("team_name_header: ", team_name_header)

    table.field_names = team_name_header

    big_d = scheduleSwap(league)
    # Iterate through all the team
    for t1 in range(len(league.teams)):
        sched = []
        # Iterate through the headers of the table
        for t2 in table.field_names:
            # If the header is empty (first col), append t1 name
            if t2 == " ":
                sched.append(league.teams[t1].team_name)
            # Else append the lookup of [t1][t1], create each row
            else:
                record = big_d[league.teams[t1].team_name][t2]
                y = "{0}-{1}-{2}".format(record[0], record[1], record[2])
                sched.append(y)
        # Add the row
        table.add_row(sched)
    # print(big_d)
    print(table)

    for trade in GetTradeActivities(league):

        team1, team2 = TradeGetTeams(trade)
        # tradeDate = GetTradeDate(trade)
        tradeWeek = TradeGetWeekBySunday(trade)
        tradeSummary = "Wk. " + tradeWeek + " " + \
            team2.team_name + " <-> " + team1.team_name
        p1 = TradeGetPlayers(trade, team1)
        p2 = TradeGetPlayers(trade, team2)

        tradeT = PrettyTable()
        tradeT.title = tradeSummary
        p_itr = 0
        team1_players = ""
        team2_players = ""
        while p_itr < len(p1) or p_itr < len(p2):
            if p_itr < len(p1) and p_itr < len(p2):
                team1_players += playerAbbreviation(p1[p_itr].name) + " "
                team2_players += playerAbbreviation(p2[p_itr].name) + " "
            if p_itr < len(p1) and p_itr >= len(p2):
                team1_players += playerAbbreviation(p1[p_itr].name) + " "
            if p_itr >= len(p1) and p_itr < len(p2):
                team2_players += playerAbbreviation(p2[p_itr].name) + "  "
            p_itr = p_itr + 1

        tradeT.field_names = [team1_players, team2_players]

        total_p1_pts = 0
        total_p2_pts = 0
        itr = int(tradeWeek)
        while itr < league.current_week:
            print("[Debug] Week: " + str(itr))

            row1 = "[Debug]["+team2.team_name+"] Week: " + str(itr) + " "
            row2 = "[Debug]["+team1.team_name+"] Week: " + str(itr) + " "
            week1_sum = 0
            week2_sum = 0
            for player in p1:
                if itr in player.stats.keys():
                    row1 += player.name + ": " + \
                        str(int(player.stats[itr]["points"])) + " "
                    total_p1_pts += player.stats[itr]["points"]
                    week1_sum += int(player.stats[itr]["points"])

            for player in p2:
                if itr in player.stats.keys():
                    row2 += player.name + ": " + \
                        str(int(player.stats[itr]["points"])) + " "
                    total_p2_pts += player.stats[itr]["points"]
                    week2_sum += int(player.stats[itr]["points"])

            print(row1)
            print(row2)
            tradeT.add_row(["Week: " + str(itr) + " " + str(int(week1_sum)),
                           "Week: " + str(itr) + " " + str(int(week2_sum))])
            itr = itr + 1
        tradeT.add_row(["Total Pts Rec: " + str(int(total_p1_pts)),
                       "Total Pts Rec: " + str(int(total_p2_pts))])
        tradeT.add_row(["Delta: " + str(int(total_p1_pts - total_p2_pts)),
                       "Delta: " + str(int(total_p2_pts - total_p1_pts))])

        tradeT.align = "c"

        print(tradeT)

        # Calculate player average pre-trade and post trade
        wk = 1
        player_avgs = {}
        while wk < league.current_week:
            #         print("[Debug] Week: " + str(j))

            for player in p1 + p2:
                if wk in player.stats.keys():
                    if player.name not in player_avgs.keys():
                        player_avgs[player.name] = [player.stats[wk]["points"]]
                    else:
                        scores = player_avgs[player.name]
                        scores.append(player.stats[wk]["points"])
                        player_avgs[player.name] = scores
            wk += 1
        print("TradeWeek: " + tradeWeek +
              " Current Week " + str(league.current_week))
        for player in player_avgs:
            pre_trade_scores = player_avgs[player][1:int(tradeWeek)-1]
            pre_trade_avg = sum(pre_trade_scores)/len(pre_trade_scores)

            post_trade_scores = player_avgs[player][int(
                tradeWeek)-1:league.current_week+1]

            if len(post_trade_scores) > 0:
                post_trade_avg = sum(post_trade_scores)/len(post_trade_scores)

                print("{} pre-trade avg: {} post-trade avg: {} ".format(player,
                      PrettyFloat(pre_trade_avg), PrettyFloat(post_trade_avg)))

        print("            ")
        print("            ")
        print("            ")


if __name__ == "__main__":
    """ This is executed when run from the command line """

    # Get environment variables
    swid = os.environ.get('SWID')
    espn_s2 = os.environ.get('ESPN_S2')
    league_id = os.environ.get('LEAGUE_ID')
    week = os.environ.get('WEEK')

    if swid == None or espn_s2 == None:
        print("SWID or ESPN_S2 environment variables empty. Exiting...")

        # Create a logger.
    logger = logging.getLogger(__name__)

# Set the output handler to a file handler that writes to a PDF file.
    file_handler = logging.FileHandler("output.pdf")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)

# Log some messages.
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

    main(swid, espn_s2, league_id, week)
