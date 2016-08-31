#!/usr/bin/python

import sys
import time
import logging
from daemon import Daemon
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


class GarageDaemon(Daemon):
    # Override constructor to accept a config dictionary
    def __init__(self, config):
        #
        # Load Configuration
        #
        self._pid = config['pid'][0]
        self._stdin = config['stdin'][0]
        self._stdout = config['stdout'][0]
        self._stderr = config['stderr'][0]
        self._client_id = config['mqtt_client_id'][0]
        self._host = config['mqtt_host'][0]
        self._port = config['mqtt_port'][0]
        self._timeout = config['mqtt_timeout'][0]
        self._proto = config['mqtt_protocol'][0]
        self._state_topic = config['state_topic'][0]
        self._cmd_topic = config['command_topic'][0]
        self._log_file = config['log_file'][0]
        #
        # Setup Logging
        #
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        fh = logging.FileHandler(self._log_file)
        self.log.addHandler(fh)
        self.log.info("Logging Initialization Complete")

        #
        # Initialize GPIOs
        #
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(26, GPIO.OUT)
        GPIO.output(26, GPIO.HIGH)
        # 1 = open, 0 = closed
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.log.info("GPIO Initialization Complete")
        #
        # Initialize Client
        #
        self.client = mqtt.Client(client_id=self._client_id, clean_session=True, protocol=mqtt.MQTTv31)
        self.log.info("MQTT Client Initialization Complete")
        #
        # Call parent constructor
        #
        super(GarageDaemon, self).__init__(self._pid, self._stdin, self._stdout, self._stderr)
        
    def run(self):
        #
        # Register Callbacks
        #
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        #
        # Connect to MQTT
        #
        self.client.connect(self._host, self._port, self._timeout)
        self.log.info("Connected to MQTT.")
        #
        # Subscribe to state/command topics
        #
        self.client.subscribe([(self._state_topic, 0),(self._cmd_topic, 0)])
        self.log.debug("Subscribed to Topics.")

        #
        # Initialize state
        #
        self.log.info("Registering initial state")
        prev_state = self.get_state()
        self.log.info(prev_state)
        publish.single(self._state_topic, payload=prev_state, hostname=self._host, protocol=mqtt.MQTTv31)
        # 
        # Loop
        #
        self.log.info("Going into main event loop")
        while True:
            try:
                self.log.info("top of loop")
                self.client.loop()
                self.log.info("In main Loop")
                #
                # Check for state change
                #
                check_state = self.get_state()
                self.log.info("back from check state, starting compare")
                if check_state != prev_state:
                    self.log.info("Sending to MQTT")
                    publish.single(self._state, payload=check_state, hostname=self._host, protocol=mqtt.MQTTv31)
                    self.log.info("Back from publish")
                    prev_state = check_state
                    self.log.info("done with checks")
                time.sleep(1)
                self.log.info("Done Sleeping")
            except:
                self.log.info("Unexpected Error: {0}".format(sys.exc_info()[0]))

    def on_connect(self, client, userdata, flags, rc):
        log = "Connected.  Result: {0}".format(rc)
        self.log.info(log)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        log = "Subscribed: {0}".format(mid)
        self.log.info(log)

    def on_message(self, client, userdata, msg):
        log = "MESSAGE Topic: {0} Message: {1}".format(msg.topic, msg.payload)
        self.log.info(log)
        if msg.topic == self._command_state:
            if msg.payload == 'ON':
                GPIO.output(26, GPIO.LOW)
                time.sleep(.5)
                GPIO.output(26, GPIO.HIGH)

    def get_state(self):
        state = GPIO.input(17)
        log = "STATE: {0}".format(state)
        self.log.info(log)
        if state:
            return "Open"
        else:
            return "Closed"

if __name__ == "__main__":
    config = {}
    configfile = 'garage.conf'
    execfile(configfile, config)
    daemon = GarageDaemon(config)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
