# SilkVeil — Privacy Through Obfuscation

from time import sleep
from shutil import copy2
from subprocess import run
from atexit import register
from os import remove, geteuid, path
from signal import SIGINT, SIGTERM, signal
from Mac import find_interface, is_valid_mac, change_mac_address
from prints import print_info, print_warning, print_success, print_error, print_banner
from Tor import TORRC_PATH, TORRC_COPY, check_tor_installed, write_bridge_config, get_obfs4_bridges, killswitch



_cleanup_done = False


INTERFACE = ""
ORG_MAC_ADDRESS = ""


def cleanup() -> None:
    global _cleanup_done
    if _cleanup_done:
        return

    ## cleanup
    print_warning("Exiting and cleaning up...")
    sleep(5)

    if INTERFACE and INTERFACE.strip():
        # set interface down
        run(
            ["ip", "link", "set", INTERFACE, "down"],
            check=True,
        )

        # set original mac address
        run(
            ["ip", "link", "set", INTERFACE, "address", ORG_MAC_ADDRESS],
            check=True,
        )

    # remove data from torrc file
    if path.exists(TORRC_COPY):
        copy2(TORRC_COPY, TORRC_PATH)
        remove(TORRC_COPY)
    else:
        print_warning(f"Backup file {TORRC_COPY} does not exist")

    if INTERFACE and INTERFACE.strip():
        # set interface up
        run(
            ["ip", "link", "set", INTERFACE, "up"],
            check=True,
        )

    #TODO:  add removing .tor directory
        # reset tor
        run(
            ["sudo", "systemctl", "restart", "tor"],
            check=True,
        )

    _cleanup_done = True
    print_success("Clean up done!")


def _handle_signal(signum, frame) -> None:
    raise SystemExit(0)  # atexit will invoke cleanup()


def setup() -> None:
    register(cleanup)
    signal(SIGINT, _handle_signal)
    signal(SIGTERM, _handle_signal)

    if geteuid() != 0:
        print_error("This tool must be run as root")
        exit()

    if not check_tor_installed():
        exit()


def main() -> None:
    global INTERFACE
    global ORG_MAC_ADDRESS
    INTERFACE, ORG_MAC_ADDRESS = find_interface()
    print_info(f"Interface: {INTERFACE}")
    print_info(f"Original mac address: {ORG_MAC_ADDRESS}")

    if not is_valid_mac(ORG_MAC_ADDRESS):
        print_error("Something went wrong with original MAC address")
        return

    change_mac_address(INTERFACE)
    sleep(3)
    write_bridge_config(get_obfs4_bridges())


if __name__ == '__main__':
    print_banner()
    setup()
    main()
    killswitch()
