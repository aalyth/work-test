#!/usr/bin/env/python3

import sys

import yaml
import json

import requests

# analogous to the C function
def errx(exit_code: int, msg: str) -> None:
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)


# result: {
#           'organization': str, 
#           'teams': {'<team1>': int, '<team2>': int, ...}
#           'users': ['<user1>', '<user2>', ...]
#         }
# terminates the script upon error
def scrape_config() -> dict:
    config = None
    with open(sys.argv[1], 'r') as config_file:
        try:
            config = yaml.safe_load(config_file)

        except:
            print('Error: could not parse yaml file.')
            sys.exit(1)

    if config is None:
        errx(1, 'Error: invalid yaml config file.')

    if type(config['organization']) is not str:
        errx(1, 'Error: invalid organization')

    if type(config['teams']) is not dict:
        config['teams'] = {}

    if type(config['users']) is not list :
        config['users'] = []
    
    return { \
            'organization': config['organization'], \
            'teams': config['teams'], \
            'users': config['users']  \
           } 


# result: {
#           '<team1>': {'<member1>': True, '<member2>': True, ...},
#           '<team2>': {'<member1>': True, '<member2>': True, ...}
#           ...
#         }
# we use dictionaries for the members so the lookup is O(1)
def scrape_team_members(config: dict) -> dict:
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {sys.argv[3]}',
    }
    org = config['organization']

    result = {}

    for team in config['teams'].keys():
        url = f'https://api.github.com/orgs/{org}/teams/{team}/members'
        
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            errx(2, f'Error: could not get "{team}" team members.')

        result[team] = {}
        for member in resp.json():
            result[team][member['login']] = True

    return result


# result: {
#           'teams': {'<team1>': int, '<team2>': int, ...}
#           'users': ['<user1>', '<user2>', ...]
#         }
def scrape_reviews(config: dict) -> dict:
    team_members = scrape_team_members(config)
    print(f'team members = {team_members}')
    
    teams = {}
    users_lookup = {} 
    users = []

    reviews = None
    with open(sys.argv[2], 'r') as reviews_file:
        try:
            reviews = json.load(reviews_file)

        except:
            errx(2, 'Error: could not parse json file.')

    def team_increment(teams: dict, team: str) -> None:
        if team not in teams:
            teams[team] = 1
        else:
            teams[team] += 1

    # rev - review
    for rev in reviews:
        try:
            user = rev['user']['login']
        except: # this part shouldn't be reached
            errx(2, 'Error: unexpected error while parsing reviews json.')

        if user in users_lookup:
            continue

        users.append(user)
        users_lookup[user] = True 

        for team, members in team_members.items():
            if user in members:
                team_increment(teams, team)
        
    return { \
            'teams': teams, \
            'users': users  \
           }

# the inputs are according to the functions above
def check_approvals(config: dict, reviews: dict) -> None:
    # lookup for the reviews['users']
    rev_usr_lookup = { x:True for x in reviews['users'] }

    for team, required in config['teams'].items():
        if team not in reviews['teams']:
            errx(3, f'Error: no reviews from the team "{team}".') 

        if reviews['teams'][team] < required:
            errx(3, f'Error: not enough approvals from team "{team}" - {reviews["teams"][team]}/{required}.')

    for usr in config['users']:
        if usr not in rev_usr_lookup:
            errx(3, f'Error: user "{usr}" has not approved.')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Error: expected 3 arguments: \n\t1- yaml config\n\t2- reviews json\n\t3- GitHub API token')
        sys.exit(1)

    config = scrape_config()
    reviews = scrape_reviews(config)

    check_approvals(config, reviews)

    sys.exit(0)
