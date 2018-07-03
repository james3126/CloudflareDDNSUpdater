# Requirements Installer v1.0ddns - James Kerley 2018
requiredPackages = ['requests','time','os','sys','json']
packageInstallNameDict = {'requests': 'requests','time': False,'os': False,'sys': False,'json': False}
missingPackages = []

def install(package):
    pip.main(['install', package])

for package in requiredPackages:
    try:
        globals()[package] = __import__(package)
    except ImportError:
        missingPackages.append(package)
        print("Failed to import %s. Will try to install..." % str(package))
    else:
        print("Imported %s" % str(package))

if len(missingPackages) > 0:
    print("\n\nAttempting to install missing packages...")
    try:
        import pip
    except ImportError:
        print("Failed...")
        sys.exit(0)
        
    for package in missingPackages:
        packageInstallName = packageInstallNameDict[package]
        print("Preparing for %s installation...\n" % str(packageInstallName))
        install(packageInstallName)

        try:
            globals()[package] = __import__(package)
        except ImportError:
            print("Unknown error at this time. Please contact me for help! Exiting...")
            exit()
        else:
            print("Imported %s" % str(package))

        print("All requirements instlled")
