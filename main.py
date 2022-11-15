#!/usr/bin/env python3
"""
Module Docstring
"""
__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import os
from prettytable import PrettyTable
from espn_api.football import League


POSITIONS = ["QB", "WR", "TE", "RB"]



def biggestBlowOut(league, week):
    outcomes = []
    
    box_scores = league.box_scores(week)
    
    for matchup in box_scores:
        diff = 0
        if matchup.home_score >= matchup.away_score:
            diff = matchup.home_score - matchup.away_score
            outcomes.append((matchup, diff))
        else:
            diff = matchup.away_score - matchup.home_score
            outcomes.append((matchup, diff))
            
    biggest_blowout, diff = sorted(outcomes, key=lambda tup: tup[1], reverse=True)[0]
    
    
    
    j = PrettyTable()
    title = "Beat that Ass Blowout".format(diff)
    j.title = title
    j.field_names=[biggest_blowout.home_team.team_name,biggest_blowout.away_team.team_name]
    j.add_row([biggest_blowout.home_score, biggest_blowout.away_score])
    j.align="c"
    print(j)

    return

def closestGame(league, week):
    outcomes = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        ## For Each Matchip calculate the diff
        diff = 0
        if matchup.home_score >= matchup.away_score:
            diff = matchup.home_score - matchup.away_score
            outcomes.append((matchup, diff))
        else:
            diff = matchup.away_score - matchup.home_score
            outcomes.append((matchup, diff))
            
    biggest_blowout, diff = sorted(outcomes, key=lambda tup: tup[1], reverse=False)[0]
    
    
    
    j = PrettyTable()
#     title = "Biggest Blowout ({0})".format(diff)
    title = "Nail Biter of the Week".format(diff)
    j.title = title
    j.field_names=[biggest_blowout.home_team.team_name,biggest_blowout.away_team.team_name]
    j.add_row([biggest_blowout.home_score, biggest_blowout.away_score])
    j.align="c"
    print(j)

    return
def biggestBenchWarmer(league, week, position):
    if position not in POSITIONS:
        return []
    
    
    benchWarmers= []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        ## For Each Matchip calculate the diff
        for player in matchup.home_lineup:
            if player.position == position and player.slot_position == "BE":
                benchWarmers.append((player.points,player.name,player.position,matchup.home_team.team_name))
                
                
        for player in matchup.away_lineup:
            if player.position == position and player.slot_position == "BE":
                benchWarmers.append((player.points,player.name,player.position,matchup.away_team.team_name))
    

    return sorted(benchWarmers, key=lambda tup: tup[0], reverse=True)

def topPlayers(league, week):
    
    topPlayers = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        ## For Each Matchip calculate the diff
        for player in matchup.home_lineup:
            if player.slot_position != "BE":
                topPlayers.append((player.points,player.name,player.position,matchup.home_team.team_name))
                
                
        for player in matchup.away_lineup:
            if player.slot_position != "BE":
                topPlayers.append((player.points,player.name,player.position,matchup.away_team.team_name))
    

    return sorted(topPlayers, key=lambda tup: tup[0], reverse=True)



def prettyPrintBenchWarmers(benchWarmers):
    x = PrettyTable()
    x.field_names = ["Points", "Player", "Team"]
    x.title = 'Biggest Benchwarmers'
    for index, warmer in enumerate(benchWarmers):
        x.add_row([warmer[0],warmer[1], warmer[3]])
    print(x)
    print("  ")
    
def prettyPrintTopScorers(benchWarmers):
    x = PrettyTable()
    x.field_names = ["Points", "Player", "Team"]
    x.title = "Top Scorers"
    for index, warmer in enumerate(benchWarmers):
        x.add_row([warmer[0],warmer[1], warmer[3]])
    print(x)
    print("  ")

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


    ## Get Best 2QBs
    for player in all_players:
        if QB > 0 and player.position == "QB":
                QB = QB - 1
                optimal_players.append(player)
                optimal_output += player.points

            
    ## Get Single FLEX Score
    for player in all_players:
        if FLEX > 0 and  (player.position == "RB" or player.position == "WR" or player.position == "TE") and (player not in optimal_players):
            FLEX = FLEX - 1
            optimal_players.append(player)
            optimal_output += player.points
     
    ## Get Best 2 RBs
    for player in all_players:
        if RB > 0 and (player.position == "RB") and (player not in optimal_players):
            RB = RB -1
            optimal_players.append(player)
            optimal_output += player.points
    
    ## Get Best WR/TE
    for player in all_players:
        if   WR_TE > 0 and (player.position == "TE" or player.position == "WR") and (player not in optimal_players):
            WR_TE = WR_TE - 1
            optimal_players.append(player)
            optimal_output += player.points
    
    return starter_ouput, optimal_output
 
    
def manager_effiency(league, week):
    manager_eff = []
    for matchup in league.box_scores(week):
            starter_ouput,optimal_output = optimalLineup(matchup.home_lineup)
            manager_eff.append((matchup.home_team.team_name,starter_ouput,optimal_output,starter_ouput/optimal_output))

            starter_ouput,optimal_output = optimalLineup(matchup.away_lineup)
            manager_eff.append((matchup.away_team.team_name,starter_ouput,optimal_output, starter_ouput/optimal_output))
            manager_eff = sorted(manager_eff, key=lambda manager_eff: manager_eff[3], reverse=True)
    return manager_eff


def prettyPrintManagerEff(manager_eff):
    
    x = PrettyTable()
    x.title = ' Galaxy Brain Manager'
    x.field_names = ["Team", "Output/Optimal", "% Accuracy"]

    manager_eff_sorted = sorted(manager_eff, key=lambda manager_eff: manager_eff[3], reverse=True)
    for manager in manager_eff_sorted[:1]:
        fraction = "{0:.0f}/{1:.0f}".format(manager[1],manager[2]) 
        percentage = "{0:.0f}".format(manager[3] * 100)
        x.add_row([manager[0], fraction,percentage])
    print(x)
    
    y = PrettyTable()
    y.title = 'Mike Zimmer Manager of the Week'
    y.field_names = ["Team", "Output/Optimal", "% Accuracy"]

    worst_manager_eff_sorted = sorted(manager_eff, key=lambda manager_eff: manager_eff[3], reverse=False)
    for manager in worst_manager_eff_sorted[:1]:
        fraction = "{0:.0f}/{1:.0f}".format(manager[1],manager[2]) 
        percentage = "{0:.0f}".format(manager[3] * 100)
        y.add_row([manager[0], fraction,percentage])
    print(y)

### Season Long Mananger Effenciey returns -> sorted list(team_name, total_output, optimal_output, accuracy %)

def seasonEffiency(league, week):
    weekly_eff = {}
    output_eff = []
    ## For Each Week Gather the Effenciey
    for i in range(1,week+1):
#         print("Week: ", i)
        weekly_eff[i] = {}
        for matchup in league.box_scores(i):
            
            starter_ouput,optimal_output = optimalLineup(matchup.home_lineup)
            weekly_eff[i][matchup.home_team.team_name] = [starter_ouput,optimal_output,starter_ouput/optimal_output]

            starter_ouput,optimal_output = optimalLineup(matchup.away_lineup)
            weekly_eff[i][matchup.away_team.team_name] = [starter_ouput,optimal_output,starter_ouput/optimal_output]
#           manager_eff.append((matchup.away_team.team_name,starter_ouput,optimal_output, starter_ouput/optimal_output))

    ## For each week for each team
    for team in league.teams:
        output = 0
        optimal = 0
        accuracy = []
        for i in range(1,week+1):
#             print(team.team_name, " ", weekly_eff[i][team.team_name])
            output += weekly_eff[i][team.team_name][0]
            optimal += weekly_eff[i][team.team_name][1]
            accuracy.append(weekly_eff[i][team.team_name][2])
            
        
        output_eff.append((team.team_name, output,optimal,sum(accuracy)/len(accuracy)))
        
    output_eff = sorted(output_eff, key=lambda output_eff: output_eff[3], reverse=True)
    return output_eff

def prettyPrintSeasonEff(total_season_eff):
    
    y = PrettyTable()
    y.title = "Total Manager Efficiency Rankings"
    y.field_names = ["Team", "Output/Optimal", "%"]
    for team in total_season_eff: 
        fraction = "{0:.0f}/{1:.0f}".format(team[1],team[2]) 
        percentage = "{0:.0f}".format(team[3] * 100)
        y.add_row([team[0], fraction,percentage])
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
    j.field_names=[saved.home_team.team_name,saved.away_team.team_name]
    j.add_row([saved.home_score, saved.away_score])
    j.align="c"
    print(j)

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
    j.field_names=[saved.home_team.team_name,saved.away_team.team_name]
    j.add_row([saved.home_score, saved.away_score])
    j.align="c"
    print(j)


def startingLineupAverage(lineup):
    starterOutput = [] 
    for player in lineup:
        if player.slot_position != "BE" and player.slot_position != "IR":
            starterOutput.append(player.points)         
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
    
    
## Team with greatest differences between max player and team average
def topHeavyTeams(league, week):
    allTeams = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        
        ## HOME TEAM
        avg = startingLineupAverage(matchup.home_lineup)
        maxPlayer = highestScoringStarter(matchup.home_lineup)
        allTeams.append((matchup.home_team.team_name, avg, maxPlayer, maxPlayer.points - avg))
        
        ## AWAY TEAM
        avg = startingLineupAverage(matchup.away_lineup)
        maxPlayer = highestScoringStarter(matchup.away_lineup)
        allTeams.append((matchup.away_team.team_name, avg, maxPlayer, maxPlayer.points - avg))
        
    allTeamSorted = sorted(allTeams, key=lambda tup: tup[3], reverse=True)
    return allTeamSorted
                                         
def prettyPrintTopHeavy(topHeavyList):
    
    j = PrettyTable()
    j.title = "One Player Wonder"
    j.field_names=["Team", "Top Player Pts", "Team Avg", "Diff"]
    for index, team in enumerate(topHeavyList[:1]):
        x="{0}: {1}".format(team[2].name,team[2].points)
        j.add_row([team[0], x, "{:.2f}".format(team[1]), "{:.2f}".format((team[2].points - team[1]))])
    print(j)


## Team with greatest differences between max player and team average
def highestTeamAverageForStarters(league, week):
    allTeams = []
    box_scores = league.box_scores(week)
    for matchup in box_scores:
        
        ## HOME TEAM
        avg = startingLineupAverage(matchup.home_lineup)
        allTeams.append((matchup.home_team.team_name, avg))
        
        ## AWAY TEAM
        avg = startingLineupAverage(matchup.away_lineup)
        maxPlayer = highestScoringStarter(matchup.away_lineup)
        allTeams.append((matchup.away_team.team_name, avg))
        
    allTeamSorted = sorted(allTeams, key=lambda tup: tup[1], reverse=True)
    return allTeamSorted

def prettyPrintHitters(hitters):
    
    j = PrettyTable()
    j.title = "Whole Team Getting Buckets"
    j.field_names=["Team", "Avg Points Per Player"]
    
    for team in hitters[:1]:
        j.add_row([team[0], "{:.2f}".format(team[1])])
        
    print(j)


def standings(league, week):
        
    j = PrettyTable()
    x = "JCPY FFL Week {0} Power Rankings".format(league.current_week)
    print(x)
    j.title = x
    
    ### Use current week - 1, so we don't calculate empty scores
    total_season_eff = seasonEffiency(league, league.current_week-1)
    
    
    j.field_names=["Ranking", "Team", "Record", " Yoff %", " Lineup IQ", "PF/PA", "# Moves", "$ Left", "Divison"]
    
    for index, tup in enumerate(league.power_rankings()):
        team = tup[1]
        
        record = "{0}-{1}-{2} {3}{4}".format(team.wins, team.losses, team.ties, team.streak_type[0], team.streak_length)
        
        ## Find Team IQ
        for i in total_season_eff:
            if i[0] == team.team_name:
                
                yoff_pct = "{0:.0f}%".format(team.playoff_pct)
                manager_iq = "{0:.0f}/{1:.0f}: {2:.0f}%".format(i[1],i[2],i[3]*100)
                pf_pa = "{0:.0f}/{1:.0f}".format(team.points_for, team.points_against)
                moves_made = team.acquisitions + team.drops + team.trades
                money_left = 100 - team.acquisition_budget_spent
                j.add_row([index+1, team.team_name,record,yoff_pct,manager_iq,pf_pa, moves_made,money_left,team.division_name])
        
    print(j)
    

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
    west_strength =sum(west_rankings)
    
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
            wins,losses,ties = 0,0,0
            for idx in range(len(op_sched)):
                if my_points[idx] > op_sched[idx]:
                    wins += 1
                elif op_sched[idx] > my_points[idx]:
                    losses += 1
                ## If the opposing schedule played me?
                elif op_sched[idx] == my_points[idx]:
                    ties += 1

            big_d[home_team.team_name][away_team.team_name] = (wins,losses,ties)     
            
    return big_d

def main(swid, espn_s2, league_id, week):
    """ Main entry point of the app """
    league = League(league_id=league_id, year=2022, espn_s2=espn_s2, swid=swid)

    ############# Final Output #################################


    week = league.current_week - 1 
    print("week: ", week)
    ## Worst Win
    worstWin(league, week)
    ## Worst Loss
    worstLoss(league, week)

    ## Biggest Blowout
    biggestBlowOut(league, week)

    ## Closest Game
    closestGame(league, week)

    ## Best and Worst Manager
    manager_eff = manager_effiency(league, week)
    prettyPrintManagerEff(manager_eff)

    ## Top Heavy
    topHeavyList = topHeavyTeams(league, week)
    prettyPrintTopHeavy(topHeavyList)

    ## Everyone was hitting
    hitters = highestTeamAverageForStarters(league,week)
    prettyPrintHitters(hitters)                                  


    qbWarmers = biggestBenchWarmer(league, week, "QB")
    rbWarmers = biggestBenchWarmer(league, week, "RB")
    teWarmers = biggestBenchWarmer(league, week, "TE")
    wrWarmers = biggestBenchWarmer(league, week, "WR")


    allWarmers = qbWarmers + rbWarmers + teWarmers + wrWarmers
    allWarmers = sorted(allWarmers, key=lambda tup: tup[0], reverse=True)
    prettyPrintBenchWarmers(allWarmers[:5])
    prettyPrintTopScorers(topPlayers(league, week)[:5])

    standings(league, week)
    divison_strength(league, week)


    
    table = PrettyTable()
    table.title = "Schedule Swap"
    table.hrules = True
    team_name_header = [" "]
    for i in range(len(league.teams)):
        team_name_header.append(league.teams[i].team_name)
    # print("team_name_header: ", team_name_header)

    table.field_names=team_name_header

    big_d = scheduleSwap(league)
    ## Iterate through all the team
    for t1 in range(len(league.teams)):
        sched = []
        ## Iterate through the headers of the table
        for t2 in table.field_names:
            ## If the header is empty (first col), append t1 name 
            if t2 == " ":
                sched.append(league.teams[t1].team_name)
            ## Else append the lookup of [t1][t1], create each row
            else:   
                record = big_d[league.teams[t1].team_name][t2]
                y = "{0}-{1}-{2}".format(record[0], record[1], record[2])
                sched.append(y)
        ## Add the row
        table.add_row(sched)
    # print(big_d)
    print(table)



if __name__ == "__main__":
    """ This is executed when run from the command line """

    # Get environment variables
    swid = os.environ.get('SWID')
    espn_s2 = os.environ.get('ESPN_S2')
    league_id = os.environ.get('LEAGUE_ID')
    week = os.environ.get('WEEK')

    if swid == None or espn_s2 == None:
        print("SWID or ESPN_S2 environment variables empty. Exiting...")


    main(swid, espn_s2, league_id, week)



