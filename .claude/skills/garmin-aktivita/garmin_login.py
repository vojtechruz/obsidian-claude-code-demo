"""Jednorazove prihlaseni do Garmin Connect a ulozeni tokenu.

Spust RUCNE v terminalu (potrebuje interaktivni vstup pro heslo a MFA):

    python ".claude/skills/garmin-aktivita/garmin_login.py"

Tokeny se ulozi do ~/.garminconnect (MIMO vault, at se tokeny nesynchronizuji ani necommituji).
Heslo se nikam neuklada. Platnost tokenu je cca 1 rok, knihovna je sama obnovuje.
"""
import os
import sys
from getpass import getpass

from garminconnect import Garmin

TOKENSTORE = os.path.expanduser("~/.garminconnect")


def main() -> int:
    email = os.getenv("GARMIN_EMAIL") or input("Garmin e-mail: ").strip()
    password = getpass("Garmin heslo: ")
    client = Garmin(email, password, prompt_mfa=lambda: input("MFA kod (z aplikace / SMS): ").strip())
    client.login(TOKENSTORE)
    name = client.get_full_name()
    print(f"OK - prihlasen jako {name}, tokeny ulozeny do {TOKENSTORE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
