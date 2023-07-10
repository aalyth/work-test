#!/usr/bin/env/python3

import sys
import yaml
import json

# analogous to the C function
def errx(exit_code: int, msg: str) -> None:
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)

class Approvals:
    groups: dict
    users: list

    def __init__(self, grps: dict, usrs: list) -> None:
        if type(grps) is not dict:
            raise TypeError

        if type(usrs) is not list:
            raise TypeError

        self.groups = grps
        self.users = usrs

    def __repr__(self) -> str:
        return f'Approvals: \n\tgroups: {self.groups} \n\tusers: {self.users} \n'


# gets the yaml config in the format: {'groups': {}, 'users': []}
# terminates the script upon error
def scrape_config() -> Approvals:
    config = None
    with open(sys.argv[1], 'r') as config_file:
        try:
            config = yaml.safe_load(config_file)

        except:
            print('Error: could not parse yaml file.')
            sys.exit(1)

    if config is None:
        errx(1, 'Error: invalid yaml config file.')

    if config['groups'] is None:
        config['groups'] = {}

    if config['users'] is None:
        config['users'] = []
    
    return Approvals(config['groups'], config['users'])

# gets the json reviews in the format: {'groups': {}, 'users': []}
# terminates the script upon error
def scrape_reviews() -> Approvals:
    groups = {}
    users_lookup = {} 
    users = []

    reviews = None
    with open(sys.argv[2], 'r') as reviews_file:
        try:
            reviews = json.load(reviews_file)

        except:
            errx(2, 'Error: could not parse json file.')


    # rev - review
    for rev in reviews:
        try:
            grp = rev['author_association']
            usr = rev['user']['login']

        # this part shouldn't be reached
        except:
            errx(2, 'Error: unexpected error while parsing reviews json.')

        if grp in groups and usr not in users_lookup:
            groups[grp] += 1
        else:
            groups[grp] = 1

        if usr not in users_lookup:
            users.append(usr)
            users_lookup[usr] = 0
        
    try:
        return Approvals(groups, users)
    except:
        errx(2, 'Error: could not parse the reviews json.')


def check_approvals(config: Approvals, reviews: Approvals) -> None:
    # lookup for the users in the reviews
    rev_usr_lookup = { x:0 for x in reviews.users }

    for grp, required in config.groups.items():
        if grp not in reviews.groups:
            errx(3, f'Error: no reviews from the group "{grp}".') 

        if reviews.groups[grp] < required:
            errx(3, f'Error: not enough approvals from group "{grp}" - {reviews.groups[grp]}/{required}.')

    for usr in config.users:
        if usr not in rev_usr_lookup:
            errx(3, f'Error: user "{usr}" has not approved.')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Error: expected 2 arguments - a yaml config file and a json with the reviews.')
        sys.exit(1)

    config = scrape_config()
    reviews = scrape_reviews()

    check_approvals(config, reviews)

    sys.exit(0)
