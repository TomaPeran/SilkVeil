from time import sleep
from requests import get
from html import unescape
from shutil import which, copy2
from os import path, access, R_OK
from subprocess import TimeoutExpired, run
from re import MULTILINE, IGNORECASE, findall
from prints import print_info, print_warning, print_success, print_error, visual_countdown


TOR_OBFS4_URL = "https://bridges.torproject.org/bridges/en?transport=obfs4"
TOR_IP_CHECK = "https://check.torproject.org/api/ip"
IP_CHECK = "https://api.ipify.org/"
TORRC_PATH = "/etc/tor/torrc"
TORRC_COPY = TORRC_PATH + "_copy"


def check_tor_installed() -> bool:
    tor_path = which("tor")
    if tor_path is None:
        print_error("Tor is not installed")
        return False

    print_success(f"Tor is installed: {tor_path}")
    try:
        result = run(
            [tor_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version = result.stdout.strip().splitlines()[0]
            print_success(version)
            return True

        print_error("Tor binary was found but could not be executed")
        return False

    except (TimeoutExpired, OSError) as e:
        print_error(f"Could not run Tor: {e}")
        return False


def check_bridges(bridges: list[str], type: str) -> bool:
    if len(bridges) != 2:
        print_error("Couldn't find obfs4 bridges")
        return False

    for bridge in bridges:
        if type == "obfs4":
            return check_obfs4_bridge(bridge)

    return False


def check_obfs4_bridge(bridge: str) -> bool:
    if "obfs4" not in bridge or "cert" not in bridge or "iat-mode" not in bridge:
            print_error("Invalid data in bridge ip configuration response")
            return False

    if len(bridge.split(' ')) != 5:
        print_warning("Invalid number of fetched data")
        return False

    return True


def get_obfs4_bridges() -> list[str] | None:
    response = get(TOR_OBFS4_URL, timeout=15).text
    matches = findall(
        r'^\s*([^<\n]+?)\s*<br\s*/?>',
        response,
        MULTILINE | IGNORECASE
    )

    matches = [
        unescape(match).strip()
        for match in matches
    ]

    if not check_bridges(bridges=matches, type="obfs4"):
        return None
    return matches


def find_obfs4proxy() -> str | None:
    obfs4proxy = which("obfs4proxy")
    if obfs4proxy is None:
       print_error("Can not find obfs4proxy command")
    return obfs4proxy


def create_torrc_copy() -> None:
    print_info(f"Torrc source exists: {path.exists(TORRC_PATH)}")
    print_info(f"Torrc source readable: {access(TORRC_PATH, R_OK)}")
    print_info(f"Fail safe Torrc destination: {TORRC_COPY}")

    try:
        copy2(TORRC_PATH, TORRC_COPY)
        print_success("Copy successful!")
    except Exception as e:
        print_warning(f"Copy failed: {type(e).__name__}: {e}")


def write_bridge_config(bridges: list[str]) -> None:

    # look for obfs4proxy, find its path
    obfs4proxy = find_obfs4proxy()
    if obfs4proxy is None or not check_bridges(bridges=bridges, type="obfs4"):
        print_error("Missing or no valid obfs4 bridges were found")
        return

    insertion_data = """UseBridges 1\nClientTransportPlugin obfs4 exec m_proxy\n\nBridge m_bridge\nBridge m_bridge\n"""
    insertion_data = insertion_data.replace("m_proxy", obfs4proxy, 1)
    for bridge in bridges:
        if not check_obfs4_bridge(bridge):
            return
        insertion_data = insertion_data.replace("m_bridge", bridge, 1)

    # create torrc fail safe copy
    create_torrc_copy()
    with open(TORRC_PATH, "a") as f_torrc:
        f_torrc.write(insertion_data)
        f_torrc.close()

    reset_tor()


def reset_tor() -> None:
    print_info("Resetting Tor")
    run(
        ["sudo", "systemctl", "restart", "tor@default"],
        check=True,
    )
    visual_countdown(60, "Waiting for service to stabilize")
    print_success("Tor is ready")# — opening Tor Browser")
    # TODO: add opening tor browser as common user
    # if not start_tor_as_logged_in_user(TORRC_PATH): # starts when output success or warning
        # # print_error("Internal problems!")
        # exit()


def killswitch() -> None:
    print_info("Fetching Tor IP address")
    try:
        response = get(
            TOR_IP_CHECK,
            proxies={
                "http": "socks5h://127.0.0.1:9050",
                "https": "socks5h://127.0.0.1:9050"
                },
            timeout=10
        ).json()
        tor_ip = response.get("IP")
    except (ValueError, KeyError) as e:
        print_error(f"Could not obtain Tor IP: {e}")
        return

    print_info(f"Given tor ip address: {tor_ip}")
    while True:
        try:
            if not response.get("IsTor"):
                print_error("Killswitch error: request is not using Tor")
                return
        except Exception as e:
            print_error(f"Killswitch error: {e}")
            return
        sleep(2)