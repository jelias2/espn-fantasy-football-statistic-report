#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Jacob Elias"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import os
from logzero import logger
from espn_api.football import League


def main(args):
    """ Main entry point of the app """
    logger.info("hello world")
    logger.info(args)


    # Get environment variables
    swid = os.getenv('SWID')
    espn_s2 = os.environ.get('ESPN_S2')

    if swid == None or espn_s2 == None:
        print("SWID or ESPN_S2 environment variables empty. Exiting...")
        return 1

    # print("SWID: ", swid)
    # print("espn_s2", espn_s2)
    # Init
    league = League(league_id=761056, year=2022, espn_s2=espn_s2,swid=swid)


    ## Get Box Scores, pass in week 
    week = 2
    if args.week != None:
        week = args.week
        

    print("Week: ", week)
    box_scores = league.box_scores(2)



    for matchup in box_scores:
        print("")
        print("Home: ", matchup.home_team, " vs. Away: ", matchup.away_team)
        print("=========================")
        print("||  ", matchup.home_score, "   ||   ", matchup.away_score)
        print("=========================")


    for team in league.teams:
        print("Team Name: ", team.team_name)
        # for player in team.Roster:
        #     player.Name



if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("arg", help="Required positional argument")

    # Optional argument flag which defaults to False
    parser.add_argument("-f", "--flag", action="store_true", default=False)

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-n", "--name", action="store", dest="ame")

    parser.add_argument("-w", "--week", action="store", dest="week")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)



