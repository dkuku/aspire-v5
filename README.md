My aspire V5 linux tools<br>
I use the provided scripts for broken backlight control on some linux laptops with intel graphics. 
When you use the scripts for backlight control don't use the acpi_backlight=vendor kernel command line.
Instructions:<br>
-for initd<br>
    put 10-sync-acpi-intel.start in /etc/local.d/ and sync-acpi-intel in /usr/local/bin<br>
    restart<br>
    check if your brightness control works (Fn + <- or ->)<br>
-for systemd<br>
    put intel.brightness.service in /etc/systemd/system/ and sync-acpi-intel-daemon.py in /usr/local/bin<br>
    enable the service : systemctl enable intel.brightness<br>
    restart<br>
    check if your brightness control works (Fn + <- or ->)
