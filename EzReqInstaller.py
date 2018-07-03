# Requirements Installer v1.1ddns - James Kerley 2018
import sys

def install(package):
    main(['install', package])

def is_new_pip():
    try:
        import pip
    except ImportError:
        print("Failed. Unknown error. Exiting...")
        exit()

    PIP_VERSION = pip.__version__

    if int(PIP_VERSION.split('.')[0]) >= 10:
        return True
    else:
        return False

def is_installed(package, attempt=1):
    try:
        globals()[package] = __import__(package)
    except ImportError:
        if attempt == 1:
            missingPackages.append(package)
            print("Failed to import %s. Will try to install..." % str(package))
        else:
            print("Unknown error at this time. Please contact me for help! Exiting...")
            exit()
    else:
        print("Imported %s" % str(package))

for package in requiredPackages:
    is_installed(package)

if len(missingPackages) > 0:
    print("\n\nAttempting to install missing packages...")

    if is_new_pip():
        from pip._internal import main

    for package in missingPackages:
        print("Preparing for %s installation...\n" % str(packageInstallName))
        install(packageInstallName)

        is_installed(package, 2)
