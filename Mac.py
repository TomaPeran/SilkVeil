from time import sleep
from re import fullmatch
from random import randint
from subprocess import PIPE, DEVNULL, run 
from prints import print_info, print_success

"""
## MAC address is valid for a NIC (unicast + not reserved/blocked ranges)

The only truly universally invalid MACs are:
-> Broadcast (FF:FF:FF:FF:FF:FF)
-> Multicast ranges (01:xx..., 33:33..., 01:00:5E...)
-> IEEE reserved control ranges (01:80:C2:00:00:xx)
-> Null (00:00:00:00:00:00, often rejected)
"""
def is_valid_mac(mac_address: str) -> bool:
    # normalize
    mac_address = mac_address.lower()

    # basic format check
    if not fullmatch(r"([0-9a-f]{2}:){5}[0-9a-f]{2}", mac_address):
        return False

    # split into bytes
    mac_bytes = [int(x, 16) for x in mac_address.split(":")]

    # 00:00:00:00:00:00 invalid
    if all(x == 0 for x in mac_bytes):
        return False

    # broadcast invalid
    if mac_address == "ff:ff:ff:ff:ff:ff":
        return False

    first_byte = mac_bytes[0]
    """
    # multicast check (LSB of first byte = 1)
    Check the least significant bit of the first byte (0X7a -> 0111 1010, LSB is 0):
       -> If it is 1 → multicast (NOK)
       -> If it is 0 → unicast (OK)
    """
    if first_byte & 1:
        return False

    """
    # IEEE reserved control range 01:80:C2:00:00:0x
    -> Spanning Tree Protocol (STP)
    -> Link Aggregation Control Protocol (LACP)
    -> Link Layer Discovery Protocol (LLDP)
    -> 802.1X authentication
    -> Bridge management frames
    """
    if mac_bytes[0:3] == [0x01, 0x80, 0xc2] and mac_bytes[3:5] == [0x00, 0X00]:
        return False

    return True


def find_current_mac(interface) -> str:
    # return os.popen("ip link show " + interface + " 2>/dev/null | grep -Eo '([a-z0-9]{2}:){5}[a-z0-9]{2} '").read().strip()
    result = run(
        ["ip", "link", "show", interface],
        stdout=PIPE,
        stderr=DEVNULL,
        text=True,
        check=False,
    ).stdout
    if "link/ether" not in result:
        return ""

    return result.split("link/ether ")[1].split()[0]


def find_interface() -> tuple[str, str] | None:
    supported_interfaces = ["eth0", "wlp1s0"]
    for interface in supported_interfaces:
        result = find_current_mac(interface).strip()
        if result != "":
            org_mac_address = result
            return interface, org_mac_address

    return None


def generate_mac_address() -> str:
    mac_address = [hex(randint(0, 255)),
                   hex(randint(0, 255)),
                   hex(randint(0, 255)),
                   hex(randint(0, 255)),
                   hex(randint(0, 255)),
                   hex(randint(0, 255))]
    return ':'.join(f"{int(x, 16):02x}" for x in mac_address)


def change_mac_address(interface: str) -> None:
    mac_address = "00:00:00:00:00:00"
    while not is_valid_mac(mac_address):
        mac_address = generate_mac_address()

    print_info(f"Changing {interface} interface MAC address")
    print_info(f"Set {interface} interface down")
    run(
        ["ip", "link", "set", interface, "down"],
        check=True
        )

    print_info(f"Change {interface} MAC address")
    run(
        ["ip", "link", "set", interface, "address", mac_address],
        check=True
    )

    print_info(f"Set {interface} interface back up")
    run(
        ["ip", "link", "set", interface, "up"],
        check=True
        )

    sleep(5)
    print_success(f"MAC address of {interface} is changed to {mac_address}")
