# Changelog
## [Unreleased] - 2026-04-29
### Changed
-  **`README.md` updated**: Project structure updated

## [Unreleased] - 2026-04-17
### Added
- **Splunk alert when sending empty logs**: Via `showActionMessage()` JS function

### Fixed
- **Empty log showing & sending**: Empty logs were shown even when no fields matched. Now if a log has nothing to show, it won't appear either be sent to Splunk

## [Unreleased] - 2026-04-08
### Added
- **Feedback when creating Splunk HEC token**: Via `showActionMessage()` JS function

### Changed
- **Splunk HEC URL**: Now it uses https instead of http
- **Dashboard Cowrie starting button**: Misconfiguration enabling Cowrie start button wrongly

## [Unreleased] - 2026-04-07
### Added
- **Splunk token creation JS**: `createSplunkToken()` JS function was missing

### Fixed
- **Splunk credentials status badge**: Creds badge was not working properly when missing token

## [Unreleased] - 2026-04-06
### Added
- **Splunk credentials configuration endpoints**: Added `POST /api/splunk/set-user` and `POST /api/splunk/set-password` to update Splunk credentials from the dashboard.
- **Splunk credentials controls in UI**: New Splunk inputs and actions in `index.html` to set username and password directly from the Home view.
- **Splunk credentials status badge**: Added a dedicated credentials status indicator (`splunk-creds`) to distinguish credentials state from token state.

### Changed
- **Splunk status payload**: `/api/splunk/status` now includes credentials-related fields (`user`, `password`, `creds`) used by the frontend to render current auth state.
- **Splunk frontend state handling**: `dashboard.js` now syncs Splunk user/password inputs from backend status and updates token/credentials badges independently.
- **Splunk send-button gating**: Logs send-to-Splunk actions now require valid credentials in addition to Splunk running state and token availability.

### Fixed
- **Credentials vs token ambiguity**: Improved backend token search flow to detect and report invalid credentials (`Unauthorized`) apart from "token not found" scenarios.

## [Unreleased] - 2026-03-31
### Added
- **Suricata full-alert export endpoint**: New backend endpoint `GET /api/suricata/every_alert` to retrieve all parsed Suricata alerts in a single request.
- **Suricata send action**: Frontend action `sendSuricataLogsToSplunk()` added to send all Suricata alerts to Splunk in one batch.

### Changed
- **Suricata selected alerts payload**: Current alerts page data is stored in hidden DOM element `suricata-logs-hidden` for selected-alert forwarding to Splunk (same as honeypots)

### Fixed
- **False error message while sending Suricata alerts**: Fixed frontend message flow to avoid showing "No valid logs to send to Splunk" after a successful send.
- - **Suricata Logs UI buttons**: Suricata & Honeypots send-to-Splunk buttons are now enabled only when Splunk is installed, running, and a token is available.

## [Unreleased] - 2026-03-27
### Added
- **Suricata CVE Details Panel**: Secondary panel (`cve-details`) shown when requesting CVE details from an alert
- **NVD API Connection**: A GET request is made to the NVD API with CVE-ID fetching more and most valuable and useful fields
- **CVE Loader Animation**: Spinning logo loader while CVE is being fetched

### Changed
- **Suricata Alerts UI**: Alert details primary panel can shift left (`slide-left`) to make room for the CVE details panel

## [Unreleased] - 2026-03-21
### Added
- **Suricata Alerts Detail**: Custom responsive overlay when clicking on any alert card
- **Alert CVE Button**: Automatically recognizes CVE and display button (non working button yet)

## [Unreleased] - 2026-03-20
### Added
- **Suricata Alert Pagination**: Stateless cursor-based pagination with 16 alers per page with `cursor_next` and `cursor_prev` instead of same pagination as Dionaea binaries (since this is a different logic) || Unlike Dionaea pagination, HoneyDash Suricata parsing recognizes files read and its reading position automatically
- **Suricata Alert Detection**: `has_next` flag in API responses to indicate if more alerts are available (pagination related)
- **Suricata Alert Parsing Fields**: Severity, protocol and timestamp (from/to not only from) range support

### Changed
- **Suricata Alert Parsing**: Improved error handling

## [Unreleased] - 2026-03-17
### Added
- **Suricata IDS Integration**: Initial Suricata manager with status detection, start/stop control and configurable binary/log paths.
- **Suricata Alerts UI**: New alerts section in Logs page with basic filters (severity/protocol) and a styled alerts grid similar to Dionaea binaries.

### Changed
- **Logs Page Layout**: Reorganized Binaries and new Alerts sections into a unified "Binaries & Alerts" block.
- **Dashboard status helper**: `updateStatusUI()` now supports optional controls (so it can be reused for Suricata without install/configure buttons).

### Fixed
- **API error responses**: Multiple endpoints now return proper HTTP 500 status codes on exceptions.
- **Dashboard custom path**: `setCustomPath()` improved to support Suricata and avoid UI runtime issues.

## [Unreleased] - 2026-03-13
### Added
- **Splunk Custom Path**: Now it is posible to manually set Splunk installation path (as Cowrie)

### Changed
- **Cowrie JS Custom Path Function**: The same function now works for both Cowrie and Splunk (instead of creating a new one)

## [Unreleased] - 2026-03-12
### Added
- **DDoSPot SSDP Log Parsing**: Full implementation with source target, maximum time and severity classification
- **DDoSPot CHARGEN Log Parsing**: Log retrieval with amplification factor calculation and severity classification
- **Amplification Factor Calculation**: Dynamic calculation for SSDP and CHARGEN based on request/response sizes (both have their response size configurated by default)
- **Severity Detection**: Automatic risk classification (low/medium/high) based on amplification factor, source target and maximum time in SSDP Logs, and packet count

### Changed
- **DDoSPot DNS severity heuristic**: Now severity also considers requests count to calculate itself

## [Unreleased] - 2026-03-10
### Added
- **DDoSPot NTP Log Parsing**: Full implementation with mode detection (client/control/monlist) and severity classification
- **DDoSPot SNMP Log Parsing**: Complete log retrieval with amplification factor calculation and severity clasification
- **Amplification Factor Calculation**: Dynamic calculation for NTP and SNMP based on request/response sizes (DNS had its own)
- **Severity Detection**: Automatic risk classification (low/medium/high) based on amplification factor (and NTP mode in NTP case)

### Changed
- **DDoSPot DNS severity**: Severity calculated field was also added to DNS logs

## [Unreleased] - 2026-03-05
### Added
- **DDoSPot Log Parsing**: Full implementation for DNS log parsing
- **DDoSPot Log Sending**: Sending DNS DDosPot logs to Splunk working
- **Dynamic JSON Construction**: Logs only include fields that exist, omitting null values

### Fixed
- **Repeated variable**: `getLogs` function was creating a repeated unnecessary variable

## [Unreleased] - 2026-03-03
### Added
- **DDoSPot Full Installation**: Automated Docker-based deployment with container creation
- **DDoSPot Port Support**: Listens on 5 ports (DNS:53 (udp/tcp), NTP:123 (udp), SNMP:161 (udp), SSDP:1900 (udp), CHARGEN:19 (udp))

### Fixed
- **Automatic Dockerfile Patching**: Fixes Alpine compatibility issues (venv, chown syntax, Python path)

## [Unreleased] - 2026-02-28
### Added
- **DDoSPot Honeypot**: Initial structure and API endpoints (status, install, start, stop)
- **DDoSPot Manager**: Created `ddospot_manager.py` skeleton with basic class structure
- **Honeypot Identification**: All honeypot logs now include `honeypot` field (cowrie/dionaea)
- **Log Type Field**: Dionaea logs now include `type` field (http/ftp/mysql) for better filtering
- **Hidden JSON Storage**: Logs stored in hidden textarea for Splunk integration

### Fixed
- **Splunk Log Sending**: Fixed misconfiguration in HTML that prevented logs from being sent to Splunk
- **Log Field Selection**: Updated field filters to include new `honeypot` and `type` fields

## [Unreleased] - 2026-02-24
### Added
- **Dionaea Binary Viewer**: Display captured malware binaries in paginated grid view (9 per page (3x3 grid))
- **Binary Metadata**: Show MD5 hash, file size, and capture timestamp for each binary
- **VirusTotal Integration**: Direct links to analyze binaries on VirusTotal using MD5 hash
- **CSS Grid Layout**: 3-column responsive grid with hover effects on binary cards and buttons
- **Pagination System**: Page-based navigation (Previous/Next arrows) with visual feedback

### Changed
- **Backend Pagination**: Simplified to 9 binaries per page using direct list slicing

### Fixed
- **Pagination Math**: Corrected index calculation from previous attempts

## [Unreleased] - 2026-02-22
### Added
- **Dionaea MySQL Log Parsing**: Full implementation for MySQL log parsing.
- **Parsing logic**: Since Dionaea saves hex characters (like \x00) as plaintext, a complex parsing logic has been required to extract correct usernames and passwords. Could be improved in future updates.
- **MySQL Log Fields**: Extract username, password, source IP and timestamp.

## [Unreleased] - 2026-02-19

### Added
- **Dionaea Log Parsing**: Full implementation for HTTP and FTP bistream log parsing
- **HTTP Log Fields**: Extract User-Agent, IP, request type, endpoint, username, password, and uploaded filenames
- **FTP Log Fields**: Parse username, password, source IP, and transferred filenames
- **Dynamic JSON Construction**: Logs only include fields that exist, omitting null values
- **Regex Pattern Matching**: Custom patterns for extracting data from literal escape sequences in logs
- **Log Type Filtering**: Support for filtering logs by service type (httpd, ftpd, mysqld)
- **Timestamp Filtering**: Query logs from specific dates onwards
- **Field Selection UI**: Checkboxes in dashboard to show/hide specific log fields
- **Log Limit Control**: Configurable number of logs to retrieve per query

### Changed
- **`_to_json()` Return Type**: Changed from returning a list to returning a single dictionary
- **Log Aggregation**: Using `append()`
- **Counter Logic**: Only increment when valid logs are found, not for every file processed
- **Conditional Field Addition**: Build log dictionaries dynamically based on available data

### Fixed
- **Cowrie logic**: Added a counter instead of limiting the final returned list size for better optimization
- **Javascript functions**: Some functions are now reused thanks to the addition of some parameters

### Technical Details
- **Bistream Directory**: Logs read from `/opt/honeydash/dionaea-data/bistreams/`
- **Log Filename Format**: Parse timestamp and service type from filename components
- **Regex Patterns**: 
  - HTTP User-Agent: `r'User-Agent: ([^\\]+)'`
  - HTTP Filename: `r'filename="([^"]+)"'`
  - FTP Username: `r'USER ([^\\]+)'`
  - FTP Password: `r'PASS ([^\\]+)'`
  - FTP File: `r'STOR ([^\\]+)'`

## [Unreleased] - 2026-02-15

### Added
- **Dionaea Docker Integration**: Complete rewrite of Dionaea management using official Docker images
- **Docker Container Management**: Automated creation, start, stop, and monitoring of Dionaea containers
- **Multi-Protocol Support**: 16 services exposed (FTP, HTTP, HTTPS, SMB, MySQL, MSSQL, SIP, MongoDB, etc.)
- **Persistent Storage**: Volumes for logs, binaries, and bistreams in `/opt/honeydash/dionaea-data/`
- **API Endpoints**: Full REST API for Dionaea control (status, install, start, stop, logs, binaries...)
- **JavaScript Functions**: `startDionaea()` and `stopDionaea()` for dashboard interaction
- **Port Mapping**: Official port configuration following Dionaea documentation (including UDP ports)

### Changed
- **Installation Method**: Switched from source compilation to Docker deployment
- **Container Name**: Using `honeydash-dionaea` for better namespace management
- **Data Directory**: Moved from `/opt/dionaea` to `/opt/honeydash/dionaea-data/`
- **Deployment Strategy**: Using `docker create` with `--restart unless-stopped` for reliability and `docker start/stop` to manage it

### Fixed
- **Python 3.13 Compatibility**: Completely avoided by using pre-built Docker images
- **Compilation Issues**: Eliminated hours of build troubleshooting with container approach
- **Module Dependencies**: No need to patch CMakeLists.txt or manage libemu/Cython
- **Service Availability**: All Dionaea services now work including Python-based protocols (HTTP, SMB, FTP, MySQL)
- **Installation Time**: Reduced from 20+ minutes (compilation) to ~2 minutes (Docker pull)

### Removed
- **Source Compilation**: Eliminated entire cmake/make/install workflow
- **Build Patching**: No longer need to modify CMakeLists.txt files
- **Manual Dependencies**: Removed apt-get installation of 15+ build packages
- **Python Package Management**: No setuptools version pinning or --break-system-packages workarounds

### Technical Details
- **DionaeaManager Class**: Rewritten to use Docker CLI via subprocess
- **Image**: `dinotools/dionaea:latest` from Docker Hub
- **Container Creation**: `docker create` with named container and restart policy
- **Volume Mounts**: 3 volumes for logs, binaries, and bistreams
- **Port Exposure**: 16 ports (13 TCP + 3 UDP) following official documentation
- **Detection Method**: Docker container name-based detection with `docker ps -a`
- **Status Monitoring**: Real-time container state checking via `docker ps --filter status=running`

### Documentation
- **README.md**: Updated prerequisites to include Docker requirement
- **README.md**: Added Docker installation instructions
- **README.md**: Simplified Dionaea feature description focusing on Docker benefits
- **README.md**: Added Dionaea API endpoints section
- **CHANGELOG.md**: Comprehensive documentation of Docker migration

## [Unreleased] - 2026-02-14

### Added
- **Dionaea Honeypot Integration**: Initial Dionaea management system with source compilation
- **Auto-compilation**: Automated build from GitHub with dependency resolution
- **CMakeLists.txt Patching**: Automatic disabling of incompatible Python and emu modules
- **Dionaea UI Card**: Dedicated dashboard card with Install/Start/Stop controls

### Changed
- **Installation Strategy**: Source compilation approach (later replaced with Docker in 2026-02-15)
- **Build Configuration**: Custom CMake configuration to skip incompatible modules

### Fixed
- **Python 3.13 Compatibility**: Attempted fixes via module disabling (switched to the Docker approach instead)

### Note
This version was tested on a Docker-based implementation on 2026-02-15. The source compilation approach failed due to several incompatibilities with Python 3.13 environments and libraries.

## [Unreleased] - 2026-02-08

### Added
- **Logs Page**: Dedicated page for Cowrie log visualization with collapsible filter sections
- **Field Selection**: Checkboxes to show/hide specific log fields (eventid, timestamp, src_ip, etc.)
- **Stacked Notifications**: Multiple messages now stack vertically without overlapping
- **Send to Splunk**: Button to forward filtered logs directly to Splunk SIEM

### Changed
- **Notification System**: Messages now use individual DOM elements with smooth slide-in/out animations
- **Message Position**: Fixed at 100px from top to remain visible below sticky header during scroll
- **Log Display**: Formatted text output with line breaks instead of raw JSON for better readability
- **Action Messages**: Extended display duration (7.4s + 7s animation) for better visibility

### Fixed
- **Notification Visibility**: Messages now stay visible when scrolling down the page
- **Line Breaks**: Added `white-space: pre-wrap` to properly display multi-line log output
- **Message Overlap**: Implemented flexbox container with gap to prevent message stacking issues

## [Unreleased] - 2026-02-06

### Added
- **Modern Web Dashboard UI**: Complete redesign with professional gradient background and card-based layout
- **Navigation Bar**: Centered navigation with Home and Logs pages, logo integration with hover effects
- **Service Cards Layout**: Grid system with 3 honeypot cards (Cowrie, Dionaea, DDoSPot) and 2-column layout for SIEM/IDS
- **Multiple Status Badges**: Display installation, running, and configuration status simultaneously per service
- **Section Dividers**: Visual separators with titles for Honeypots, SIEM, and IDS sections
- **Responsive Design**: Adaptive grid layout (3 columns → 2 columns → 1 column based on screen size)
- **Footer**: Copyright and branding information

### Changed
- **Card Actions Layout**: Reorganized buttons into logical rows with full-width distribution
- **Cowrie Controls**: Separated Install/Configure/Restore, Start/Stop, and Path/Status controls into distinct rows
- **Status Badge Styling**: Closely grouped badges with minimal spacing, right-aligned for standard cards
- **Suricata Card Alignment**: Right-to-left text alignment with reversed badge order for visual symmetry
- **Background Pattern**: Added subtle diagonal pattern overlay for depth without distraction
- **Color Scheme**: Updated to golden/brown gradient (#a88100 to #433100) with improved contrast

### Technical Details
- **CSS Grid System**: `repeat(3, 1fr)` for honeypots, `repeat(2, 1fr)` for SIEM/IDS section with `.two-columns` class
- **Flexbox Navigation**: Centered nav with `position: absolute` and `transform: translateX(-50%)`
- **Badge Grouping**: `margin-left: 0.5rem` for tight spacing, reversed with `margin-right` for Suricata
- **Card Hover Effects**: `translateY(-5px)` elevation with enhanced shadows
- **Blur/shadow Filter**: Blur and shadow effects on header and cards.

## [Unreleased] - 2026-02-05

### Added
- **Splunk SIEM Integration**: Complete Splunk management with status monitoring, service control, and HEC token operations
- **HEC Token Management**: Automatic creation and retrieval of HTTP Event Collector tokens for event forwarding
- **Event Forwarding**: Send Cowrie logs to Splunk with configurable sourcetype and index
- **Log Retrieval API**: Query Cowrie JSON logs with filtering by limit, event_id, and timestamp
- **Batch Event Processing**: Handle multiple events efficiently with error tracking and partial success reporting
- **SSL Warnings Suppression**: Disabled urllib3 warnings for self-signed certificates in local Splunk instances

### Changed
- **Cowrie Detection Optimization**: Added `-quit` flag to `find` command for immediate exit after first match
- **Detection Timeout Strategy**: Reduced `/opt` search timeout to 5s, separate timeout handling for global search
- **Log Response Format**: Filter and return only relevant fields (eventid, timestamp, src_ip, username, password, etc.)
- **Event Payload Parsing**: Extract logs from nested `{"logs": [...]}` structure before sending to Splunk
- **API Documentation**: Updated with Splunk endpoints and Cowrie log retrieval query parameters

### Fixed
- **Timeout Exception Handling**: Wrapped `/opt` search in try-except to continue with global search on timeout
- **Find Output Issue**: Added `-print` flag before `-quit` to ensure results are displayed before exit
- **Event Structure Problem**: Fixed event parsing to handle dictionary with "logs" key instead of raw array

### Technical Details
- **SplunkManager Class**: New manager in `siem/splunk_manager.py` with REST API communication
- **Base64 Authentication**: Uses basic auth with admin credentials for Splunk management API
- **HEC Communication**: Proper header formatting with `Splunk <token>` authorization
- **Error Aggregation**: Tracks failed events separately while reporting successful sends

## [Unreleased] - 2026-02-03

### Added
- **Web Dashboard**: HTML frontend with real-time status monitoring for testing (auto-refresh every 5s)
- **Non-root execution**: Cowrie runs as unprivileged user via `sudo -u $SUDO_USER`
- **Security validation**: Application must be run with `sudo` from non-root user (blocks direct root execution)
- **SSH service detection**: Tries both `sshd` and `ssh` services, suppresses errors when service doesn't exist
- **Auto-cleanup on exit**: SIGINT handler automatically restores SSH configuration and removes iptables rules

### Changed
- **Cowrie detection**: Two-phase search strategy (common path /opt first, then global search with 10s timeout)
- **Detection method**: Uses `find` command searching for unique `honeyfs` directory instead of fixed paths
- **Configuration management**: Section-based parsing for `cowrie.cfg` to modify only `[ssh]` section, leaving `[telnet]` and others intact
- **SSH port regex**: Fixed pattern from `^Port+\s*\d*` to `^Port\s+\d+` for proper port line detection
- **Virtualenv PATH**: Uses `sudo -u user env PATH=... VIRTUAL_ENV=...` to preserve virtualenv when dropping privileges

### Fixed
- **Subprocess conflicts**: Removed conflicting `capture_output` and `stderr` parameters
- **Find command returncode**: Check `stdout.strip()` instead of `returncode` (find returns 1 on permission denied even with results)
- **Flask double execution**: Added `use_reloader=False` to prevent initialization running twice
- **SSH restart errors**: Redirect stderr to DEVNULL to suppress "Unit sshd.service not found" messages
- **Privilege check logic**: Use `SUDO_USER` environment variable to distinguish `sudo` execution from direct root login

### Technical Details
- **Detection validation**: Checks for `bin/`, `honeyfs/`, and `etc/` directories to confirm valid Cowrie installation
- **Port configuration**: Regex-based section parsing ensures only SSH listen_endpoints is modified
- **Environment preservation**: Passes virtualenv PATH via `env` command when using `sudo -u`

### Removed
- Dedicated system user creation (`cowrie` user) - now uses original sudo user instead
