#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import csv
import sys

import requests
from bs4 import BeautifulSoup


def main():
    page = 1
    url = "https://www.barrfoundation.org/grantmaking/grants/page/"

    with open("data.csv", "w", newline="") as f:
        fieldnames = ["grantee", "grantee_url", "description", "Award Date",
                      "Amount", "Term", "Program"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            print("Doing page", page, file=sys.stderr)
            r = requests.get(url + str(page))

            soup = BeautifulSoup(r.content, "lxml")

            # We have gone past the last page, so stop
            grants = soup.find_all("div", {"class": "GrantCard"})
            if len(grants) <= 0:
                break

            for grant in grants:
                d = {}
                grantee = grant.find("h2", {"class": "GrantCard-organization"})
                d["grantee"] = grantee.text.strip()

                # The grantee URL might not exist, so just ignore if it doesn't
                # exist.
                try:
                    d["grantee_url"] = grantee.find("a").get("href")
                except AttributeError:
                    pass

                d["description"] = grant.find("p", {"class": "GrantCard-description"}).text.strip()
                for li in grant.find_all("li", {"class": "GrantCard-info-item"}):
                    fieldname = li.find("b").text.strip()
                    value = li.text.strip()[len(fieldname):].strip()
                    assert fieldname.strip(":") in fieldnames
                    d[fieldname.strip(":")] = value

                writer.writerow(d)

            page += 1


if __name__ == "__main__":
    main()
