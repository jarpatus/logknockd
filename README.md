# logknockd
Logknockd is a simple "log knocking" daemon which monitors given logfile and runs commands when sequence of matches are detected. One use case would be monitoring firewall logs and opening access when given sequence of "port knocks" are detected, but you may find other use cases as well (enable ssh access after login has failed in a row for defined sequence of users, in addition to port knocking? or something totally else :).

# Why 
Was looking for port knocking daemon for OpenWrt, but knockd seems to be abandoned and more advanced fwknopd lacks up to date Android client and is too abandoned. Other options tried to directly modify iptables which is a huge mess since nftables are now used etc. So had to write yet another solution.

# Installation
Clone:
```
git clone https://github.com/jarpatus/logknockd.git logknockd
```

No additional python packages needed. For OpenWrt python3-light is enough. This is why we do polling etc. instead of fancy inotify or so packages.

# Configuration
Customize logknockd.conf for your needs (it's JSON). Top level properties:
* ```file``` - File to watch i.e. /var/log/system.log
* ```ruleset``` - Array of rules which do work indepedently

Rule properties:
* ```name``` - Name of the rule
* ```filter``` - High level filter (regular expression) which must be matched or row will be ignored. Regular expression must have one capturing group which "groups" rows together. I.e. for firewall logs source IP could be used so if logs are bombarded with port scans your own port knocking sequence will still be identifiable.
* ```sequence``` - Array of filters which must be matched in correct sequence in order for commands to be ran. Capturing groups can be used to capture information for the commands to be ran.
* ```cmds``` - Array of commands to be ran if sequence was completed. Captured groups from last match are used as parameters, {0}, {1}, {2}... can be used in command to represent captured values.

# Clients
Simple port knocking clients do exist for many platforms. E.g. for Android Knock on Ports seem to work well.

# Examples

## OpenWrt
Make OpenWrt to log to a file i.e. /tmp/system.log. Optionally make firewall to drop instead of reject (example uses drop). Create port forwarding firewall rules. Then use configuration like this:
```
{
  "file": "/tmp/system.log",
  "ruleset": [
    {
      "name": "Open ports",
      "filter": "drop wan in: .* SRC=([0-9.]+) .* PROTO=UDP",
      "sequence": [
        "drop wan in: .* SRC=([0-9.]+) .* DPT=1234",
        "drop wan in: .* SRC=([0-9.]+) .* DPT=5678",
        "drop wan in: .* SRC=([0-9.]+) .* DPT=8765",
        "drop wan in: .* SRC=([0-9.]+) .* DPT=4321"
      ],
      "cmds": [
        "uci set firewall.cfgxxx.src_ip={0}",
        "uci set firewall.cfgxxx.enabled=1",
        "uci commit"
      ]
    }
  ]
}
```

This will match port knocking sequence 1234, 5678, 8765, 4321 and then will enable and update port forwarding rule to allow traffic from you IP. Idea is not to mess with iptables or nftables directly but to toggle and modify ready made firewall rules.

# Security
* Notice that port knocking is kind of securty by obscurity and should not be used as primary security method. It should be used as additional method only.
* For port knocking purposes we cannot inspect packet contents (unlike knockd) nor can we do as advanced security as fwknopd does. So this is very simple daemon but for many use cases more than enough.
* Do not run any crazy commands which could open more security holes. Enabling existing firewall rule could be ok.
* Generally know what you are doing. Don't blame me if something bad happens.

# TODO
* There are no "timeout" mechanism which could e.g. automatically disable port forwarding after a while. 
