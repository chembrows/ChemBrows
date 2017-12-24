# Linux

I had problems with the version of GLIBC, 2.26 on Arch and 2.23 on Ubuntu. I
packaged the software on Ubuntu to make sure it would run on this platform.


# Windows

ed25519 was compiled from the source (github). Scipy was installed from a dled
wheel. Numpy, pyhook and pywin32 as well. UPX in setup.spec was turned to
False.


# Debugging

Use empty excludes and rm_bins lists in setup.spec if the software doesn't
start. On Windows, turn bool "console" in setup.spec to True to get the logs.
