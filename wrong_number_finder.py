"""Script to find phone numbers assoiated with an address(s)."""
import pprint
import re
import itertools
import time
import pandas
import requests
import phonenumbers
from googlesearch import search
from bs4 import BeautifulSoup
from requests import HTTPError


def search_timer(things, time_per_thing, overhead, min_time=3):
    """Estimates the seconds it may take to complete a task.

    Parameters
    ----------
    things : TYPE
        DESCRIPTION.
    time_per_thing : TYPE
        DESCRIPTION.
    overhead : TYPE
        DESCRIPTION.
    min_time : TYPE, optional
        DESCRIPTION. The default is 3.

    Returns
    -------
    None.

    """
    if (things*(time_per_thing+overhead)) < min_time:
        run_time = min_time
    else:
        run_time = REC_COUNT*(DELAY+RUN_FACT)
    return run_time


REGEX = r"\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b"
# The secret sauce
results = {}
my_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/68.0.3440.106 Safari/537.36'
HEADERS = {
    'User-Agent': (my_user_agent)
}
REC_COUNT = 5
DELAY = 2
RUN_FACT = 1.7

# targets and parms || will be prompted for in future
doc_path = r"C:\Users\andrew.white\Documents\Lists\CPC\Wong Numbers Jan 2020"
file_name = "Wrong Number DB Jan 2020.xlsx"
full_path = r"{doc}\{file}".format(doc=doc_path, file=file_name)
ws_name = "Worksheet"
worksheet = pandas.read_excel(full_path, sheet_name=ws_name)
addresses_to_find = worksheet["Full Address"]

if REC_COUNT < 0:
    things_to_look_up = addresses_to_find
    REC_COUNT = len(addresses_to_find)
    print("Allons-y... should be about {run_time} secs"
          .format(run_time=search_timer(REC_COUNT, DELAY, RUN_FACT)))
else:
    things_to_look_up = itertools.islice(addresses_to_find, 0, REC_COUNT + 1)
    print("Allons-y... should be about {run_time} secs"
          .format(run_time=search_timer(REC_COUNT, DELAY, RUN_FACT)))

start_time = time.time()

for address in things_to_look_up:
    try:
        urls_found = search(address, pause=DELAY, stop=10,
                            user_agent=my_user_agent)
        entry = list(urls_found)
        count = len(entry)
        pprint.pprint("{count} urls for {address} added to results..."
                      .format(count=count, address=address))
        results[address] = entry
    except HTTPError as err:
        print("Oops... {error}".format(error=err))

s_count = 0
for s in results.values():
    s_count = s_count+len(s)

print("Search complete... {count} found".format(count=s_count))
print("--- Total seach time %s seconds ---" % (time.time() - start_time))
for k, r in results.items():
    for u in r:
        try:
            data_got = requests.get(u, HEADERS)
        except Exception:
            pass
        b = data_got.text
        soup = BeautifulSoup(b, 'html.parser')
        for node in soup.findAll('body'):
            matches = re.finditer(REGEX, str(node.findAll(text=True)),
                                  re.MULTILINE)
            phone_numbers_found = {}
            phone_numbers_found = set()
            for matchNum, match in enumerate(matches, start=1):
                # print("Match {matchNum} was found at {start}-{end}:{match}"
                #       .format(matchNum=matchNum, start=match.start(),
                #               end=match.end(), match=match.group()))
                if match.group() in phone_numbers_found:
                    print("Gotz it...")
                else:
                    phone_numbers_found.add(match.group())
                    print("{x} numbers for {address} found so far"
                          .format(x=len(phone_numbers_found), address=k))
                    results[k]

print(("Total of {things} address(s) searched for.\nRetrived {count} \
       urls.\nYeilding {numbers} phone numbers.")
      .format(things=len(results), count=s_count,
              numbers=len(phone_numbers_found)))
out = pandas.DataFrame.from_dict(results, orient="index")
out.to_csv("numbers.csv")
