import urllib.parse
import argparse
import requests
import sys
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--mode", help="Put on or of home mode. 0 is home, 1 is away", required=True, type=int)
    parser.add_argument(
        "-u", "--username", help="Username to cloud.leakomatic.com", required=True)
    parser.add_argument(
        "-p", "--password", help="Password to cloud.leakomatic.com", required=True)
    parser.add_argument(
        "-d", "--device", help="Device id to target. Can be seen in the path of the request that looks like \"/devices/[your-ID]/change_mode.json\" when changing mode.", required=True, type=int)
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

    csrfCookie = r.cookies.get_dict().get('XSRF-TOKEN')
    if csrfCookie is None:
        print("Failed getting CSRF token, exiting")
        sys.exit(1)

    modeUrl = f"https://cloud.leakomatic.com:443/devices/{args.device}/change_mode.json"
    modeHeaders = {"Content-Type": "application/json;charset=UTF-8",
                   "X-Xsrf-Token": urllib.parse.unquote(csrfCookie), "User-Agent": "Mozilla/5.0", "Connection": "close"}
    modeJson = {"mode": args.mode}
    r2 = s.post(modeUrl, headers=modeHeaders, json=modeJson)

    if r2.status_code == 200:
        print("Successfully changed mode")
    else:
        print("Did not get the expected HTTP status code, something went wrong")
        sys.exit(1)


if __name__ == "__main__":
    main()
