#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import csv
import datetime
import re

def mysql_quote(x):
    """Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    our input is fixed and from a basically trustable source."""
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)


def main():
    with open("data.csv", "r") as f:
        reader = csv.DictReader(f)
        first = True

        print("""insert into donations (donor, donee, amount, donation_date,
        donation_date_precision, donation_date_basis, cause_area, url,
        donor_cause_area_url, notes, affected_countries, affected_states,
        affected_cities, affected_regions) values""")

        for row in reader:
            amount = row['Amount']
            assert amount.startswith("$"), amount
            amount = amount.replace("$", "").replace(",", "")

            # These grantees have a grant amount of $0 for some reason. The
            # assertion is here to make sure we know all such grantees.
            zero_amounts = ['Farm Africa USA, Inc.', 'George Washington University']
            assert int(amount) or row['grantee'] in zero_amounts, (amount, row['grantee'])
            donee = row['grantee']
            donee = re.sub(r",? inc\.?$", "", donee, flags=re.IGNORECASE)
            donation_date = datetime.datetime.strptime(row['Award Date'], "%m/%d/%Y").strftime("%Y-%m-%d")

            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Barr Foundation"),  # donor
                mysql_quote(donee),  # donee
                amount,  # amount
                mysql_quote(donation_date),  # donation_date
                mysql_quote("day"),  # donation_date_precision
                mysql_quote("donation log"),  # donation_date_basis
                mysql_quote("FIXME"),  # cause_area
                mysql_quote("https://www.barrfoundation.org/grantmaking/grants/"),  # url
                mysql_quote("FIXME"),  # donor_cause_area_url
                mysql_quote(row['description']),  # notes
                mysql_quote(""),  # affected_countries
                mysql_quote(""),  # affected_states
                mysql_quote(""),  # affected_cities
                mysql_quote(""),  # affected_regions
            ]) + ")")
            first = False
        print(";")

if __name__ == "__main__":
    main()
