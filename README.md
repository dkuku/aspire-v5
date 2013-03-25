My aspire V5 linux tools
I use the provided scripts for broken backlight control on some linux laptops with intel graphics. 
When you use the scripts for backlight control don't use the acpi_backlight=vendor kernel command line.
Instructions:
put 10-sync-acpi-intel.start in /etc/local.d/ and sync-acpi-intel in /usr/local/bin
restart
check if your brightness control works (Fn + <- or ->)
