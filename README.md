# SilkVeil

Linux privacy networking utility for automated Tor + obfs4 configuration and network identity management.
SilkVeil is a Linux-based Python utility designed to automate several privacy-oriented network configuration tasks. It combines MAC-address randomization, Tor configuration, obfs4 bridges, and fail-safe cleanup into a single command-line workflow.

### Disclaimer: 
SilkVeil is an experimental privacy/security project. It does not guarantee anonymity or protection against all forms of network monitoring, fingerprinting, traffic analysis, or endpoint compromise.

## Features
### MAC address randomization
Detects the active network interface.
Stores the original MAC address.
Generates and applies a randomized MAC address.
Restores the original address during cleanup.
### Tor integration
Verifies that Tor is installed and available.
Configures Tor to use obfs4 bridges.
Locates the obfs4proxy executable.
Restarts the Tor service after configuration.
### obfs4 bridge support
Retrieves obfs4 bridge information from the Tor BridgeDB.
Validates received bridge configuration.
Injects valid bridge configuration into torrc.
### Fail-safe configuration
Creates a backup of the existing Tor configuration before modification.
Restores the original torrc during cleanup.
Handles SIGINT and SIGTERM to trigger cleanup when the program exits.
### Tor connectivity verification
Uses the Tor SOCKS proxy to verify external connectivity.
Checks whether requests are passing through the Tor network.
## Architecture
                         ┌──────────────────┐
                         │     SilkVeil     │
                         └────────┬─────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
        ┌────────────────┐ ┌──────────────┐ ┌───────────────┐
        │ MAC Management │ │ Tor Manager  │ │ Signal/Cleanup│
        └───────┬────────┘ └──────┬───────┘ └───────┬───────┘
                │                 │                 │
                ▼                 ▼                 ▼
          Network NIC        obfs4 bridges      Restore state
                │                 │
                │                 ▼
                │              torrc
                │                 │
                └────────┬────────┘
                         ▼
                    ┌─────────┐
                    │   Tor   │
                    └────┬────┘
                         │
                         ▼
                      Internet

## Workflow

SilkVeil follows a setup/cleanup lifecycle:

1. Verify root privileges
        ↓
2. Verify Tor installation
        ↓
3. Detect network interface
        ↓
4. Save original MAC address
        ↓
5. Generate and apply randomized MAC
        ↓
6. Retrieve and validate obfs4 bridges
        ↓
7. Backup torrc
        ↓
8. Configure Tor
        ↓
9. Restart Tor
        ↓
10. Verify Tor connectivity
        ↓
      Runtime
        ↓
11. Restore network/Tor configuration

## Requirements

SilkVeil currently targets Linux systems and requires:

- Python3
- Tor
- obfs4proxy
- iproute2
- systemd
- Root privileges
- Python requests package

The system must also have a compatible network interface that SilkVeil can manage.

## Installation

Clone the repository:
```
git clone https://github.com/TomaPeran/SilkVeil.git
cd SilkVeil
```

Install the Python dependency:
```
pip install requests
```

Make sure Tor and obfs4proxy are installed and available in PATH.

## Usage

Run SilkVeil with root privileges:
```
sudo python3 main.py
```

The application will:

- Detect the network interface.
- Record the original MAC address.
- Generate a randomized MAC address.
- Retrieve and validate obfs4 bridges.
- Back up the existing Tor configuration.
- Configure Tor.
- Restart Tor.
- Verify Tor connectivity.

Press Ctrl+C to terminate the program and trigger the cleanup procedure.

## Project Structure
```
SilkVeil/
├── main.py
├── Mac.py
├── Tor.py
├── prints.py
├── torrc.sample.in
└── README.md
```
main.py

Coordinates the application lifecycle, signal handling, setup, cleanup, and execution flow.

### Mac.py

Responsible for:

- Network interface discovery
- MAC address validation
- Random MAC generation
- MAC address modification
### Tor.py

Responsible for:

- Tor installation checks
- obfs4 bridge retrieval
- Bridge validation
- torrc modification
- Tor service management
- Tor connectivity verification
- prints.py

Contains terminal output and status-display helpers.

## Security Model

SilkVeil is intended as an automation and privacy-hardening tool, not as a complete anonymity solution.

Changing a MAC address affects the local Layer-2 network identity of the interface. Tor provides network-level privacy for applications that actually send their traffic through Tor.

These mechanisms do not prevent:

- Application-level fingerprinting
- Browser fingerprinting
- Malware or endpoint compromise
- DNS or traffic leaks caused by applications outside Tor
- User-account identification
- Behavioral identification
- Traffic analysis performed by sufficiently capable observers

For this reason, SilkVeil should be considered a privacy configuration utility rather than an anonymity guarantee.

## Design Considerations

A major design goal is to avoid leaving the system in a partially modified state.

Before modifying the Tor configuration, SilkVeil creates a backup of the existing torrc.

During cleanup, the application attempts to:

Restore the original MAC address.
Restore the original Tor configuration.
Restart the Tor service.
Return the network interface to its previous operational state.

Signal handlers are registered for SIGINT and SIGTERM so that normal interruption can trigger the cleanup process.

## TODO
- [ ] Improve network interface detection and support arbitrary interface names instead of relying on predefined interfaces.
- [ ] Implement a proper firewall-based network killswitch to prevent non-Tor traffic from leaving the system.
- [ ] Improve failure recovery so partially completed setup operations are safely rolled back.
- [ ] Add automated tests for MAC address generation/validation, bridge parsing, and configuration handling.
- [ ] Improve Tor/obfs4 configuration management and validate the resulting configuration before restarting Tor.
- [ ] Add structured logging and configurable verbosity for easier debugging and troubleshooting.
- [ ] Improve temporary file and Tor data cleanup during shutdown and unexpected failures.
- [ ] Add support for configurable network and Tor settings through command-line arguments or a configuration file.
## Technologies

Python · Linux · Tor · obfs4 · Linux Networking · systemd · iproute2 · Network Privacy · Subprocess Management

## Disclaimer

SilkVeil is provided for educational, research, and privacy-testing purposes.

The author does not guarantee anonymity, security, or protection against network monitoring. Users are responsible for understanding the limitations of Tor, MAC randomization, and their operating environment.
