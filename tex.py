#!/usr/bin/env python
import os
import sys
import time
import json
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Optional


class SlackRequester:
    def __init__(self, url: Optional[str]):
        self.url = url

    def send_message(self, message: str):
        slack_response = requests.request("POST", self.url, json={"text": message})


class Monitor:
    def __init__(self):
        # TODO paramterize headless
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        # self.driver = webdriver.Chrome()

        # TODO parameterize this some way
        self.apartments = {
            "Sorrel": {
                "base_url": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/?beds=2",
                "rooms": [
                    {
                        "units": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/floorplans/401080619/?beds=2&moveInDate=",
                        "size": 1279,
                        "beds": 2,
                    },
                    {
                        "units": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/floorplans/401080618/?beds=2&moveInDate=",
                        "size": 1103,
                        "beds": 2,
                    },
                ],
            },
            "Camden Panther Creek": {
                "base_url": "https://www.camdenliving.com/frisco-tx-apartments/camden-panther-creek/apartments?move-in=3-months&bedrooms=all",
                "rooms": [
                    {
                        "units": "https://www.camdenliving.com/frisco-tx-apartments/camden-panther-creek/532/15-oct-3-2020",
                        "size": 800,
                        "beds": 1,
                    },
                    {
                        "units": "https://www.camdenliving.com/frisco-tx-apartments/camden-panther-creek/1331/16-sep-26-2020",
                        "size": 1170,
                        "beds": 2,
                    },
                    {
                        "units": "https://www.camdenliving.com/frisco-tx-apartments/camden-panther-creek/837/16-sep-26-2020-0",
                        "size": 795,
                        "beds": 1,
                    },
                ],
            },
            "Bexley": {
                "base_url": "https://www.bexleywestridge.com/floorplans.aspx",
                "rooms": [
                    {
                        "units": "https://www.bexleywestridge.com/availableunits.aspx?myOlePropertyId=924407&MoveInDate=&t=0.013835374545229762&floorPlans=2603032",
                        "size": 760,
                        "beds": 1,
                    },
                    {
                        "units": "https://www.bexleywestridge.com/availableunits.aspx?myOlePropertyId=924407&MoveInDate=&t=0.9055206899474619&floorPlans=2603035",
                        "size": 840,
                        "beds": 1,
                    },
                    {
                        "units": "https://www.bexleywestridge.com/availableunits.aspx?myOlePropertyId=924407&MoveInDate=&t=0.8321057805663594&floorPlans=2603038",
                        "size": 1169,
                        "beds": 2,
                    },
                ],
            },
            "Cortland Phillips Creek": {
                "base_url": "https://cortland.com/apartments/cortland-phillips-creek-ranch/floorplans/",
                "rooms": [
                    {
                        "units": "https://cortland.com/apartments/cortland-phillips-creek-ranch/floorplans/b1/#content",
                        "size": 1105,
                        "beds": 2,
                    },
                    {
                        "units": "https://cortland.com/apartments/cortland-phillips-creek-ranch/floorplans/a5/#content",
                        "size": 984,
                        "beds": 1,
                    },
                ],
            },
        }

    def update_prices(self):
        for location_name, location_info in self.apartments.items():
            base_url = location_info["base_url"]
            rooms = location_info["rooms"]
            # TESTING
            sorrel_str = ""
            # SORREL
            for room in rooms:
                sorrel_str += f"==================\nSorrel - {room['size']}sqft\n{room['units']}\n==================\n"
                self.driver.get(room["units"])
                self.driver.refresh()

                # TODO conditional element locators
                # sorrel locator
                # TODO change this from arbitrary wait to retry
                time.sleep(2)  # need to wait here
                wrapper = self.driver.find_element_by_class_name(
                    "floorplan-unit-wrapper"
                )
                for unit in wrapper.find_elements_by_class_name("unit-info"):
                    sorrel_str += f"{unit.text}\n\n"
            # print(sorrel_str)
            self.driver.close()
            return sorrel_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # TODO add headless flag
    parser.add_argument("--poll", type=int, default=10)
    args = parser.parse_args()

    current_directory = os.path.dirname(os.path.realpath(__file__))
    with open(f"{current_directory}/config.json") as json_file:
        config_data = json.load(json_file)
    slack_webhook_url = config_data.get("webhook_url")
    slack_requester = SlackRequester(slack_webhook_url)

    m = Monitor()
    sorrel = m.update_prices()
    print(sorrel)
    if slack_requester.url is not None:
        slack_requester.send_message(
            f"<!channel> Testing sorrel scraper ```{sorrel}```"
        )
