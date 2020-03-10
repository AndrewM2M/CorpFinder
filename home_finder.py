from urllib import parse
from googleapiclient.discovery import build
from googleapiclient import errors as google_err
from fuzzywuzzy import fuzz, process
import sys
import tldextract
from tqdm import tqdm


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def progress_by_step(current, total, step):
    step_count = 100//step
    stops = [round((step*x), 2) for x in range(step_count)]
    percent = round((current/total)*100, 2)
    if current != 0 and int(percent) in stops:
        print(f"{current} of {total} -- reached [{round(percent)}%]")

def finder(target, api_key, cse, result_keys):
    google_data = {}
    home_pages = {}
    tc = len(target)
    print(f"{tc} targets to look up...")
    max_c = input("Do all?[y/n][number]")
    if not max_c.isnumeric():
        if max_c != "y" and "Y":
            sys.exit("bye!")
        else:
            max_c = tc
    else:
        max_c = int(max_c)
    print(f"Proceding with {max_c}", end="... ")
    itter = zip(range(max_c), target)
    for c, t in tqdm(itter, total=max_c):
        try:
            results = google_search(f'{t} homepage', api_key, cse, num=1)
            google_data[t] = {key: results[0][key] for key in result_keys}
            # progress_by_step(c, max_c, 10)
        except google_err.HttpError:
            print("Quota exceded processing findings")
    for k in google_data.keys():
        link = tldextract.extract(
            parse.urlparse(google_data[k]["link"]).netloc)
        match = fuzz.token_sort_ratio(k, link.domain)
        match_str =\
            "Strong" if match > 60 else "Suspect" if match > 40 else "Week" \
            if match > 20 else "Bad"
        home_pages[k] = (google_data[k]["link"], match_str, match)
        # found_one = {}
        # remnants = {}
        # for k, result in enumerate(results):
        #     if fuzz.token_set_ratio(result["title"], t) == 100:
        #         found_one = results.pop(k)
        #         results.clear()
        #     else:
        #         if fuzz.token_set_ratio(result["title"], t) < 90:
        #             results.remove(result)
        # if len(found_one) < 1:
        #     for k, remaining in enumerate(results):
        #         vals = list(remaining.values())
        #         # print(vals)
        #         remnants[k] = vals
        #     rem_keys = list(remnants.keys())
        #     rem_vals = list(remnants.values())
        #     # print(rem_vals)
        #     best_guess = process.extractOne(t, rem_vals,
        #                                     scorer=fuzz.token_set_ratio)
        #     guess_key = rem_keys[rem_vals.index(best_guess[0])]
        #     print(f"Best guess for {t} is {results[guess_key]['link']}")
        #     found[t] = "guess:"+results[guess_key]['link']
        #     continue
        #     if best_guess not in suspects.values():
        #         try:
        #             key = rem_keys[rem_vals.index(best_guess[0])]
        #             suspects[key] = best_guess
        #         except ValueError:
        #             print(best_guess, "\nnot found, moving on")
        # print(suspects)
        try:
            print(f"For {k} found: {home_pages[k]}")
        except KeyError:
            print(f"no link for {k}")
    return home_pages
