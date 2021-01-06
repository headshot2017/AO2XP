import platform

def get_hdid():
    os = platform.system()

    if os == "Windows": # what a mess...
        import _winreg
        registry = getattr(_winreg, "\x48\x4b\x45\x59\x5f\x4c\x4f\x43\x41\x4c\x5f\x4d\x41\x43\x48\x49\x4e\x45")
        address = "\x53\x4f\x46\x54\x57\x41\x52\x45\x5c\x4d\x69\x63\x72\x6f\x73\x6f\x66\x74\x5c\x43\x72\x79\x70\x74\x6f\x67\x72\x61\x70\x68\x79"
        keyargs = _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY
        key = _winreg.OpenKey(registry, address, 0, keyargs)
        value = _winreg.QueryValueEx(key, "\x4d\x61\x63\x68\x69\x6e\x65\x47\x75\x69\x64")
        _winreg.CloseKey(key)
        return value[0]

    elif os == "Linux":
        return os.popen("cat /var/lib/dbus/machine-id").read().rstrip()
    
    elif os == "Darwin": # https://gist.github.com/erikng/46646ff81e55b42e5cfc
        import objc
        from Foundation import NSBundle

        IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

        functions = [("IOServiceGetMatchingService", b"II@"),
                     ("IOServiceMatching", b"@*"),
                     ("IORegistryEntryCreateCFProperty", b"@I@@I")
                    ]

        objc.loadBundleFunctions(IOKit_bundle, globals(), functions)
        keyname = "IOPlatformSerialNumber"
        return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("IOPlatformExpertDevice")), keyname, None, 0)

    else:
        return "(%s) no u jm" % os
