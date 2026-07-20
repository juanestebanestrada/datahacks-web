import requests, json
res = requests.get("http://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard").json()
if "events" in res and len(res["events"]) > 0:
    for event in res["events"][:1]:
        comp = event["competitions"][0]
        if "odds" in comp:
            print("Odds keys:", comp["odds"][0].keys())
            print(comp["odds"][0])
