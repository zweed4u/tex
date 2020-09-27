#!/usr/bin/env python
import os
import sys
import time
import json
import argparse
import datetime
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
        # start-maximized flag doesnt work in headless - makes sense; instead explicitly set
        # options.add_argument("--start-maximized")
        options.add_argument("--window-size=1440x900")

        self.driver = webdriver.Chrome(options=options)
        self.driver.delete_all_cookies()

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
                        "units": "https://www.camdenliving.com/frisco-tx-apartments/camden-panther-creek/932/16-sep-27-2020",
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
        self.latest_run_duration = None
        self.previous_initial_map = self.update_prices()
        self.updated_map = None

    def update_prices(self):
        start_time = time.time()
        apt_map = dict()
        for location_name, location_info in self.apartments.items():
            base_url = location_info["base_url"]
            rooms = location_info["rooms"]
            apt_map[location_name] = dict()

            if location_name == "Sorrel":
                print(f"{datetime.datetime.now()} :: Sorrel parsing...")
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
                            apt_map[location_name].update({size: price.split()[-1]})

            elif location_name == "Camden Panther Creek":
                print(f"{datetime.datetime.now()} :: Camden Panther Creek parsing...")
                for room in rooms:
                    # TODO handle benign modal
                    self.driver.get(room["units"])
                    rent_total = self.driver.find_element_by_class_name(
                        "rent-total-amount"
                    )
                    fees = self.driver.find_elements_by_class_name("fee-amount")
                    rent = fees[0].text
                    description = self.driver.find_element_by_class_name(
                        "card.unit-info"
                    ).text

                    size = description.splitlines()[1]
                    # lmao this check isnt even needed becuase we're using
                    # room specific urls but okay I guess...
                    if f"{room['size']}" in size:
                        # beds = description.splitlines()[2]
                        # baths = description.splitlines()[3]
                        apt_map[location_name].update({size: rent})

            elif location_name == "Bexley":
                print(f"{datetime.datetime.now()} :: Bexley parsing...")
                for room in rooms:
                    self.driver.get(room["units"])
                    time.sleep(1)
                    table = self.driver.find_element_by_class_name(
                        "availableUnits.table.table-bordered.table-striped.table-responsive"
                    )
                    for unit in table.find_elements_by_class_name("AvailUnitRow"):
                        size = unit.find_element_by_css_selector(
                            "td[data-label='Sq. Ft.']"
                        ).text
                        price_range = unit.find_element_by_css_selector(
                            "td[data-label='Rent']"
                        ).text
                        min_price = price_range.split("-")[0]
                        price_as_num = int(min_price.replace("$", "").replace(",", ""))
                        current_cheapest = int(
                            apt_map[location_name]
                            .get(size, "$9,999")
                            .replace("$", "")
                            .replace(",", "")
                        )
                        if price_as_num < current_cheapest:
                            apt_map[location_name].update({size: min_price})

            elif location_name == "Cortland Phillips Creek":
                print(
                    f"{datetime.datetime.now()} :: Cortland Phillips Creek parsing..."
                )
                for room in rooms:
                    self.driver.get(room["units"])
                    size = self.driver.find_element_by_class_name(
                        "floorplan-single__meta"
                    ).text
                    rent = self.driver.find_element_by_class_name(
                        "floorplan-single__price-text"
                    ).text
                    size_sq_ft = size.split("| ")[-1]
                    price = rent.split()[-1]
                    apt_map[location_name].update({size_sq_ft: price})

        self.latest_run_duration = time.time() - start_time
        return apt_map

    def update_and_compare(self):
        is_changed = False
        if self.previous_initial_map is None:
            return "Unable to compare - previous map was none"
        # TODO - use get() for check and fault tolerance
        updated_map = self.update_prices()
        compare_report_string = ""
        for location, location_room_info in updated_map.items():
            for size, price in location_room_info.items():
                updated_rooms_num_price = int(
                    price.replace("$", "").replace(",", "").split(".")[0]
                )
                previous_rooms_num_price = int(
                    self.previous_initial_map[location][size]
                    .replace("$", "")
                    .replace(",", "")
                    .split(".")[0]
                )
                compare_report_string += f"[*{location} - {size}*] size room price "
                if updated_rooms_num_price != previous_rooms_num_price:
                    is_changed = True
                    price_difference = abs(
                        updated_rooms_num_price - previous_rooms_num_price
                    )
                    if updated_rooms_num_price > previous_rooms_num_price:
                        compare_report_string += "increased :arrow_up: "
                    else:
                        compare_report_string += "decreased :arrow_down: "
                    compare_report_string += (
                        f"by *${price_difference}*! Was: *${previous_rooms_num_price}* "
                    )
                else:
                    compare_report_string += f"has remained the same. "
                compare_report_string += (
                    f"- Currently: *${updated_rooms_num_price}*\n\n"
                )
        self.previous_initial_map = updated_map
        return (compare_report_string, is_changed)

    def close_browser(self):
        self.driver.close()


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        # TODO add headless flag
        parser.add_argument("--poll", type=int, default=60)
        args = parser.parse_args()

        current_directory = os.path.dirname(os.path.realpath(__file__))
        with open(f"{current_directory}/config.json") as json_file:
            config_data = json.load(json_file)
        slack_webhook_url = config_data.get("webhook_url")
        slack_requester = SlackRequester(slack_webhook_url)

        m = Monitor()
        running = True
        while running:
            print()
            time.sleep(args.poll)
            try:
                report, price_update = m.update_and_compare()
                if slack_requester.url is not None:
                    mention = ""
                    if price_update:
                        mention += "<!channel> "
                    slack_requester.send_message(
                        f"{mention}Latest headless scrape took {m.latest_run_duration}s\n:moneybag: Price Update Report :moneybag:\n{report}\n"
                    )
            except Exception as exc:
                print(f"Subsequent lookup failed in update and comparison: {exc}")
                running = False

        m.close_browser()
    except:
        m.close_browser()
