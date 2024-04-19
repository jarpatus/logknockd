# logknockd
Logknockd is a simple "log knocking" daemon which monitors given logfile and runs commands when sequence of matches are detected. One use case would be monitoring firewall logs and opening access when given sequence of "port knocks" are detected, but you may find other use cases as well.

# Why 
Was looking for port knocking daemon for OpenWrt, but knockd seems to be abandoned and more advanced fwknopd lacks up to date Android client. Other options tried to directly modify iptables which is a huge mess etc. So had to write yet another solution.

# How
