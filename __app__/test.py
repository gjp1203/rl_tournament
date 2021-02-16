"""
"""

import os
import requests

import subprocess

# CONST_TEAMS_LIST = ["team1", "team2", "team3", "team4", "team5", "team_test"]
CONST_TEAMS_LIST = ["team_test"]
CONST_GITHUB_ADDRESS = (
    "https://raw.githubusercontent.com/"
    + "alan-turing-institute/rl_tournament/main/teams/"
)
CONST_DOCKER_COMPOSE_TEMPLATE = "docker-compose.yml_template"
CONST_TOURNAMENT_FILE = "/tmp/tournament.txt"
CONST_TEMP_DOCKER_COMPOSE = "/tmp/docker-compose.yml"


def get_team_repository_tags(team_name):
    """
    Get the list tags (agents) for a team

    Arguments:
        team_name - team's name

    Returns:
        tags - a list of tags
    """

    address = "%s%s.txt" % (CONST_GITHUB_ADDRESS, team_name)

    req = requests.get(address)

    tags = req.content.decode("UTF-8").lower().split()

    return tags


def create_tournament():
    """
    Creates a tournament file.

    """

    pelicans = []
    panthers = []

    for team in CONST_TEAMS_LIST:
        tags = get_team_repository_tags(team)

        if len(tags) > 0:

            for tag in tags:

                if "pelican" in tag:
                    pelicans.append("%s:%s" % (team, tag))
                elif "panther" in tag:
                    panthers.append("%s:%s" % (team, tag))

    pelicans = list(set(pelicans))
    panthers = list(set(panthers))

    f = open(CONST_TOURNAMENT_FILE, "w")

    for pelican in pelicans:
        for panther in panthers:

            f.write("%s %s\n" % (pelican, panther))

    f.close()


def run_tournament():
    """
    Runs the tournament by running multiple docker-compose files
    """

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    template_path = os.path.join(path, CONST_DOCKER_COMPOSE_TEMPLATE)

    with open(template_path, "r") as file:
        template = file.read()

    with open(CONST_TOURNAMENT_FILE, "r") as file:
        matches = file.read().splitlines()

    for match in matches:

        match_yaml = template

        pelican, panther = match.split()

        match_yaml = match_yaml.replace("<<PELICAN>>", pelican)
        match_yaml = match_yaml.replace("<<PANTHER>>", panther)

        with open(CONST_TEMP_DOCKER_COMPOSE, "w") as file:
            file.write(match_yaml)

        cwd = os.getcwd()

        os.chdir("/tmp")

        subprocess.Popen(["docker-compose", "up"])

        # check the database for match results
        import time

        time.sleep(20)
        # when to stop the process?

        subprocess.run(["docker-compose", "down"])

        os.chdir(cwd)


def clean_up():
    """
    Clean up after the tournament
    """

    os.remove(CONST_TOURNAMENT_FILE)
    # os.remove(CONST_TEMP_DOCKER_COMPOSE)


if __name__ == "__main__":

    create_tournament()

    run_tournament()

    clean_up()

    print("Finished")