import urllib.parse
import argparse
import requests
import json
import sys
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--username", help="Username to cloud.leakomatic.com", required=True)
    parser.add_argument(
        "-p", "--password", help="Password to cloud.leakomatic.com", required=True)
    parser.add_argument(
        "-d", "--device", help="Device id to target. Can be seen in the path of the request that looks like \"/devices/[your-ID]/change_mode.json\" when changing mode.", required=True, type=int)
    parser.add_argument(
        "-s", "--home-status", help="Print if in away or home mode", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "-a", "--alarm-status", help="Print the alarm status. \"Alarm\" if there currently is an alarm, \"No alarm\" otherwise", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "-j", "--json", help="Print the raw json", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--disable-json-beatify", help="Don't beatify the json, just print it on one row", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    s = requests.Session()
    csrfUrl = s.get("https://cloud.leakomatic.com/login")
    result = re.search(
        r"<meta name=\"csrf-token\" content=\"([A-Za-z0-9+/=]*)\"", csrfUrl.text)
    authToken = result.group(1)
    if authToken == "" or authToken is None:
        print("Did not get auth token, exiting")
        sys.exit(1)

    loginUrl = "https://cloud.leakomatic.com:443/login"
    loginHeaders = {"Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0"}
    loginPostData = {"utf8": "\xe2\x9c\x93", "authenticity_token": authToken,
                     "user[email]": args.username, "user[password]": args.password, "user[remember_me]": "0", "commit": "Log in"}
    r = s.post(loginUrl, headers=loginHeaders,
               data=loginPostData, allow_redirects=False)

    csrfCookie = r.cookies.get_dict().get('_website_session')
    if csrfCookie is None:
        print("Failed getting session cookie, exiting")
        sys.exit(1)

    statusUrl = f"https://cloud.leakomatic.com/devices/{args.device}.json"
    r2 = s.get(statusUrl)

    if r2.status_code != 200:
        print("Did not get the expected HTTP status code, something went wrong")
        sys.exit(1)

    if args.json:
        indent = 2
        if args.disable_json_beatify:
            indent = 0
        print(json.dumps(r2.json(), indent=indent))
    if args.home_status:
        status = r2.json().get("mode")
        if status is None:
            print("Did not get any status")
            sys.exit(1)
        if status == 0:
            print("Home")
        elif status == 1:
            print("Away")
        else:
            print("Got unknown status")
            sys.exit(1)

    if args.alarm_status:
        status = r2.json().get("alarm")
        if status is None:
            print("Did not get any status")
            sys.exit(1)
        if status:
            print("Alarm")
        else:
            print("No alarm")


if __name__ == "__main__":
    main()
