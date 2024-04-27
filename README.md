# logknockd
Logknockd is a simple "log knocking" daemon which monitors given logfile and runs commands when sequence of matches are detected. One use case would be monitoring firewall logs and opening access when given sequence of "port knocks" are detected, but you may find other use cases as well (enable ssh access after login has failed in a row for defined sequence of users, in addition to port knocking? or something totally else :).

# Why 
Was looking for port knocking daemon for OpenWrt, but knockd seems to be abandoned and more advanced fwknopd lacks up to date Android client and is too abandoned. Other options tried to directly modify iptables which is a huge mess since nftables are now used etc. So had to write yet another solution.

# Installation
Clone:
```
git clone https://github.com/jarpatus/logknockd.git logknockd
```

Python 3 is needed, no additional packages required. For OpenWrt python3-light is enough. This is why we do polling etc. instead of fancy inotify or so packages.

# Configuration
Copy logknockd.conf from examples/ to the same directory where logknockd.py resides. Customize for your needs (it's JSON). Top level properties:
* ```trace``` - Enable trace logging - do not use lightheartly, espeially if logging goes to the same log which is monitored as infinite loop will occur
* ```debug``` - Enable debug logging
* ```file``` - File to watch i.e. /var/log/system.log
* ```ruleset``` - Array of rules which do work indepedently

Rule properties:
* ```name``` - Name of the rule
* ```filter``` - High level filter (regular expression) which must be matched or row will be ignored. Regular expression must have one capturing group which "groups" rows together. I.e. for firewall logs source IP could be used so if logs are bombarded with port scans your own port knocking sequence will still be identifiable.
* ```sequence``` - Array of filters which must be matched in correct sequence in order for commands to be ran. Capturing groups can be used to capture information for the commands to be ran.
* ```actions``` - Array of commands to be ran if sequence was completed. Captured groups from last match are used as parameters, {0}, {1}, {2}... can be used in command to represent captured values.

# Clients
Simple port knocking clients do exist for many platforms. E.g. for Android Knock on Ports seem to work well.

# Guides

## OpenWrt
* Make OpenWrt to log system log to /tmp/system.log, from System -> System -> Logging -> Write system log to file.
* Make firewall to drop packets instead of reject, from Network -> Firewall -> Zones -> wan. Optional but update filters in case of reject.
* Make firewall to log dropped / rejected packets,  from Network -> Firewall -> Zones -> wan -> Edit -> Advanced settings -> Enable logging on this zone
* Create some port forwards
* Use configuration example from examples/openwrt/logknockd.conf, customize based on your needs. Idea is not to mess with iptables or nftables directly but to update firewall rules with correct sourcer IP.
* Copy examples/openwrt/logknockd.init to /etc/init.d/logknockd and enable service.

# Security
* Notice that port knocking is kind of securty by obscurity and should not be used as primary security method. It should be used as additional method only.
* For port knocking purposes we cannot inspect packet contents (unlike knockd) nor can we do as advanced security as fwknopd does. So this is very simple daemon but for many use cases more than enough.
* Do not run any crazy commands which could open more security holes. Enabling existing firewall rule could be ok.
* Generally know what you are doing. Don't blame me if something bad happens.

# TODO
* There are no "timeout" mechanism which could e.g. automatically disable port forwarding after a while. 
