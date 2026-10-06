from time import sleep

RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
CYAN = "\033[36m"


banner = """
        ╔═════════════════════════════════════════════════════════════╗
        ║  ███████╗██╗██╗     ██╗  ██╗██╗   ██╗███████╗██╗██╗         ║
        ║  ██╔════╝██║██║     ██║ ██╔╝██║   ██║██╔════╝██║██║         ║
        ║  ███████╗██║██║     █████╔╝ ██║   ██║█████╗  ██║██║         ║
        ║  ╚════██║██║██║     ██╔═██╗ ╚██╗ ██╔╝██╔══╝  ██║██║         ║
        ║  ███████║██║███████╗██║  ██╗ ╚████╔╝ ███████╗██║███████╗    ║
        ║  ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝╚══════╝    ║
        ║                                                             ║
        ║                     CUSTOM NETWORK TOOL                     ║
        ║            weave connections • veil your traffic            ║
        ╚═════════════════════════════════════════════════════════════╝
    """


def print_banner() -> None:
    print(f"{BOLD}{CYAN}{banner}{RESET}")
    sleep(1)


def print_error(msg: str) -> None:
    print(f"{BOLD}{RED}[-] {msg}{RESET}")
    sleep(1)


def print_warning(msg: str) -> None:
    print(f"{BOLD}{YELLOW}[!] {msg}{RESET}")
    sleep(1)


def print_success(msg: str) -> None:
    print(f"{BOLD}{GREEN}[+] {msg}{RESET}")
    sleep(1)


def print_info(msg: str) -> None:
    print(f"{BOLD}{CYAN}[i] {msg}{RESET}")
    sleep(1)


def visual_countdown(seconds: int, msg: str ="Countdown") -> None:
    for number in range(seconds, -1, -1):
        print(f"\r{msg}: {number:2}", end="", flush=True)
        sleep(1)
    print()
