#!/usr/bin/python3
import os
import json
import argparse
import requests
from typing import Optional


class SlackRequester:
    def __init__(self, url: Optional[str]):
        self.url = url

    def send_message(self, message: str):
        slack_response = requests.request("POST", self.url, json={"text": message})


class Monitor:
    def __init__(self):
        # TODO parameterize this some way
        self.apartments = {
            "Sorrel": {
                "url": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/?beds=2",
                "rooms": [
                    {"size": 1279, "beds": 2},
                    {"size": 1103, "beds": 2},
                ],
            },
            "Camden Panther Creek": {
                "url": "https://www.camdenliving.com/frisco-tx-apartments/camden-panther-creek/apartments?move-in=3-months&bedrooms=all",
                "rooms": [
                    {"size": 800, "beds": 1},
                    {"size": 1170, "beds": 2},
                    {"size": 795, "beds": 1},
                ],
            },
            "Bexley": {
                "url": "https://www.bexleywestridge.com/floorplans.aspx",
                "rooms": [
                    {"size": 760, "beds": 1},
                    {"size": 840, "beds": 1},
                    {"size": 1169, "beds": 2},
                ],
            },
            "Cortland Phillips Creek": {
                "url": "https://cortland.com/apartments/cortland-phillips-creek-ranch/floorplans/",
                "rooms": [
                    {"size": 1105, "beds": 2},
                    {"size": 984, "beds": 1},
                ],
            },
        }

    def update_prices(self):
        for location_name, location_info in self.apartments.items():
            url = location_info["url"]
            rooms = location_info["url"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poll", type=int, default=10)
    args = parser.parse_args()

    current_directory = os.path.dirname(os.path.realpath(__file__))
    with open(f"{current_directory}/config.json") as json_file:
        config_data = json.load(json_file)
    slack_webhook_url = config_data.get("webhook_url")
    slack_requester = SlackRequester(slack_webhook_url)

    m = Monitor()
    if slack_requester.url is not None:
        slack_requester.send_message(
            f"<!channel> This is a nightmare :astonished: ```{json.dumps(m.apartments, indent=4)}```"
        )
