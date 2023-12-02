# Autorun Handler for Harmony.AI Plugin
# Set flag "autostart" in harmony.ini to "1" to trigger autostart of Harmony.AI

import time
from threading import Thread, current_thread
from harmony import load_config, start


class DelayedLaunchThread(Thread):

    def __init__(self, game, autostart_delay):
        # execute the base constructor
        Thread.__init__(self)
        # set config vars
        self.game = game
        self.autostart_delay = autostart_delay

    def run(self):
        time.sleep(self.autostart_delay)
        start(self.game)


def start_autorun(game):
    # Get Basic Config from harmony.ini
    config = load_config()
    autostart = int(config.get('Harmony', 'autostart'))
    # Perform autostart if flag is set
    if autostart > 0:
        autostart_delay = int(config.get('Harmony', 'autostart_delay'))
        # Create Thread to wait for launch without blocking other startup processes
        launch_trigger = DelayedLaunchThread(game, autostart_delay)
        launch_trigger.run()
        print("Harmony.AI: Autostart enabled. Starting in {0} seconds".format(autostart_delay))
    else:
        print("Harmony.AI: Autostart disabled.")



