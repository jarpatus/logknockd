# logknockd
Logknockd is a simple "log knocking" daemon which monitors given logfile and runs commands when sequence of matches are detected. One use case would be monitoring firewall logs and opening access when given sequence of "port knocks" are detected, but you may find other use cases as well.

# Why 
Was looking for port knocking daemon for OpenWrt, but knockd seems to be abandoned and more advanced fwknopd lacks up to date Android client. Other options tried to directly modify iptables which is a huge mess etc. So had to write yet another solution.

# Installation
Clone:
```
git clone https://github.com/jarpatus/logknockd.git logknockd
```

Create python virtual environment and install dependencies: 
```
cd logknockd
python3 -m venv venv
source venv/bin/activate
pip3 install python-config-parser watchfiles
```

# Configuration
Customize logknockd.yaml for your needs. Top level configuration options:
* file - File to watch i.e. /var/log/system.log
* ruleset - Array of rules which do work indepedently

Rule options:
* name - Name of the rule
* filter - High level filter (regular expression) which must be matched or row will be ignored. Regular expression must have one capturing group which "groups" rows together. I.e. for firewall logs source IP could be used so if logs are bombarded with port scans your own port knocking sequence will still be identifiable.
* sequence - Array of filters which must be matched in correct sequence in order for commands to be ran. Capturing groups can be used to capture information for the commands to be ran.
* cmds - Array of commands to be ran if sequence was completed. Captured groups from last match are used as parameters, {0}, {1}, {2}... can be used in command to represent captured values.




