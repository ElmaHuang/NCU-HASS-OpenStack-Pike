import libvirt

Event_string = (
    ("Added", "Updated"),
    ("Removed"),
    ("Booted", "Migrated", "Restored", "Snapshot", "Wakeup"),
    ("Paused", "Migrated", "IOError", "Watchdog", "Restored", "Snapshot"),
    ("Unpaused", "Migrated", "Snapshot"),
    ("Shutdown", "Destroyed", "Crashed", "Migrated", "Saved", "Failed", "Snapshot"),
    ("Finished")
)

Event_failed = (Event_string[5][2], Event_string[5][5])

Event_watchdog_action = (
    libvirt.VIR_DOMAIN_EVENT_WATCHDOG_NONE,  # = 0, No action, watchdog ignored
    libvirt.VIR_DOMAIN_EVENT_WATCHDOG_PAUSE,  # = 1, Guest CPUs are paused
    # libvirt.VIR_DOMAIN_EVENT_WATCHDOG_RESET,       # = 2, Guest CPUs are reset
    libvirt.VIR_DOMAIN_EVENT_WATCHDOG_POWEROFF,  # = 3, Guest is forcibly powered off
    libvirt.VIR_DOMAIN_EVENT_WATCHDOG_SHUTDOWN,  # = 4, Guest is requested to gracefully shutdown
    libvirt.VIR_DOMAIN_EVENT_WATCHDOG_DEBUG,  # = 5, No action, a debug message logged
    libvirt.VIR_DOMAIN_EVENT_WATCHDOG_INJECTNMI,  # = 6, Inject a non-maskable interrupt into guest
)
