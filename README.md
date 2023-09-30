# Key-Logger
 A simple keylogger to gather data locally for analysing possible keyboard layouts

Based on the tutorial at https://www.askpython.com/python/examples/python-keylogger

## Setup
Windows Defender Antivirus picks this up - it needs to be manually allowed to be able to run/not get deleted;
To exclude the folder on my version of Windows 11 (and to change it back again later) go to:
Settings -> Windows Security settings -> Virus & Threat Protection -> Virus  & threat protections settings (header) -> Manage settings -> Exclusions -> Add or remove exclusions

To run on startup, make a shortcut to main.pyw and add it to your startup folder or add the file to the windows registry (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)

## To Do
- [ ] log key up and key down separately
- [ ] save logs in dated files within a logs folder