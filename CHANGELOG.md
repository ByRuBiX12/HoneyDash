# Changelog

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
