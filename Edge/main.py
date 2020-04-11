from connection import MessagingService, Wifi, MqttConnection
from services import Ntp, EnvironmentMonitor, Triangulation

wifi = Wifi("AndroidAP", "vaqz2756")
mqtt = MqttConnection("broker.hivemq.com", wifi)

messaging_service = MessagingService(wifi)
messaging_service.add_channel(mqtt)

ntp_service = Ntp(wifi)
environment_service = EnvironmentMonitor(wifi, mqtt, messaging_service)
triangulation_service = Triangulation(wifi, mqtt)


# Channels:
#   has_pending_messaged -> bool
#   transmit -> bool (to abort)? void?

# This will run in its own thread and use a lock to be notified of when new
# messages are posted and network is available

# Imagine a method for pushing a new message. This method is called by the
# scheduling thread and will check if network is available, and release a lock
# owned by the scheduling thread
#   Then the messaging thread can continue and begin publishing messages on
#   wifi (assuming the triangulation job does not hold the wifi lock for
#   scanning)
#   While the messaging thred is transmitting data, it holds the lock
#   previously held by the scheduling thread. Whenever network is lost or it
#   runs out of pending messages, the lock is released for the scheduling
#   thread to hold.
#   So we should have a lock for using the wifi resource. It should also not be
#   possible to publish messages while the message handling thread holds the
#   lock mentioned above.
# The reason for this architecture is that it should bring down the stack depth
# needed for securely transmitting data without data loss. This depth introduces
# overhead to the regular processing.

# A lock is used for synchronizing scheduling and messaging. It is held by either the
# scheduler or the messager, never both. The messager can only operate when it holds the
# lock. The scheduler can operate without it, but must wait when trying to publish new messages.
