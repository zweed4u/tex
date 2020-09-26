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
        # options.headless = True
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)

        # TODO parameterize this some way
        self.apartments = {
            "Sorrel": {
                "base_url": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/",
                "rooms": [
                    {
                        "units": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/floorplans/401100123/?beds=2&moveInDate=",
                        "size": "1,279",
                        "beds": 2,
                    },
                    {
                        "units": "https://www.sorrelpcr.com/apartments/tx/frisco/floor-plans#/floorplans/401100095/?beds=2&moveInDate=",
                        "size": "1,103",
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
            if location_name == "Sorrel":
                s_map = {location_name: dict()}
                sorrel_str = ""
                self.driver.get(base_url)
                # TODO remove arbitrary wait - spinner on table load
                time.sleep(1)
                table = self.driver.find_element_by_class_name("table-margin-bottom")
                for row in table.find_elements_by_class_name("table-row"):
                    for room in rooms:
                        newline_delimeted_row = row.text.splitlines()
                        size = newline_delimeted_row[3]
                        if room["size"] in size:
                            # beds = newline_delimeted_row[1]
                            # baths = newline_delimeted_row[2]
                            price = newline_delimeted_row[4]
                            s_map[location_name].update({size: price.split()[-1]})

            #     sorrel_str += f"==================\nSorrel - {room['size']}sqft\n{room['units']}\n==================\n"
            #     self.driver.get(room["units"])
            #     time.sleep(1)
            #     self.driver.refresh

            #     # TODO conditional element locators
            #     # sorrel locator
            #     # TODO change this from arbitrary wait to retry
            #     time.sleep(2)  # need to wait here
            #     wrapper = self.driver.find_element_by_class_name(
            #         "floorplan-unit-wrapper"
            #     )
            #     for unit in wrapper.find_elements_by_class_name("unit-info"):
            #         sorrel_str += f"{unit.text}\n\n"
            # # print(sorrel_str)
            self.driver.close()
            return s_map
            # return sorrel_str


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
    if slack_requester.url is not None:
        slack_requester.send_message(
            f"<!channel> simplified sorrel scraper: ```{json.dumps(sorrel, indent=4)}```"
        )
