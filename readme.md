# FIRST SETUP
This selinux policy module can be used in two modes:
* access clamd via TCP on port 3310 (preferrably on localhost)
* access clamd via the local socketfile in /run/clamd.scan/clamd.sock ( /etc/clamd.d/scan.conf has to use the same path as the /etc/c-icap/clamd_mod.conf !)

For now both ways to access the antivirus software are allowed by the SELinux.
For the future I might add a seboolean (getsebool -a -> setsebool -P something=on/off) for this.

Other than that it should run straight out of the box.

# Finished RPMs
You can find the finished RPMs in my small repository under https://dev.techno.holics.at/technoholics-repo/

# Cheers!

