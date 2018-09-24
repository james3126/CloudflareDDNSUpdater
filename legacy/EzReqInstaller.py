# Requirements Installer v1.3ddns - James Kerley 2018
def install(PACKAGE):
    main(['install', PACKAGE])

def is_new_pip():
    try:
        import pip
    except ImportError:
        print("Failed. Unknown error. Exiting...")
        exit()

    return bool(int(pip.__version__.split('.')[0]) >= 10)

def is_installed(PACKAGE, ATTEMPT=1):
    try:
        globals()[PACKAGE] = __import__(PACKAGE)
    except ImportError:
        if ATTEMPT == 1:
            MISSING_PACKAGES.append(PACKAGE)
            print("Failed to import %s. Will try to install..." % str(PACKAGE))
        else:
            print("Unknown error at this time. Please contact me for help! Exiting...")
            exit()
        return False
    else:
        print("Imported %s" % str(PACKAGE))
        return True

def get_required():
    REQUIRED_PACKAGES = []
    FILE = open("requirements.txt", "r")
    for LINE in FILE:
        REQUIRED_PACKAGES.append(LINE)

    return REQUIRED_PACKAGES

REQUIRED_PACKAGES = get_required()
MISSING_PACKAGES = []

for PACKAGE in REQUIRED_PACKAGES:
    if not is_installed(PACKAGE):
        MISSING_PACKAGES.append(PACKAGE)
        
if len(MISSING_PACKAGES) > 0:
    print("\n\nAttempting to install missing packages...")

    if is_new_pip():
        from pip._internal import main

    for PACKAGE in MISSING_PACKAGES:
        print("Preparing for %s installation...\n" % str(PACKAGE_INSTALL_NAME))
        install(PACKAGE_INSTALL_NAME)

        is_installed(PACKAGE, 2)
