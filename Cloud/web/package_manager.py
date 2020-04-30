import mqtt
import string
import random
from repository import ontology_context

def __generate_id():
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=12
        )
    )

def assign_package(device_id: str, package_type: str):
    package_id = __generate_id()
    mqtt.set_package_id(device_id, package_id)
    ontology_context.insert_package_to_device(device_id,package_id,package_type)

    # TODO: Look up setpoints for package type in ontology
    setpoints = ontology_context.get_setpoints_on_packagetype(package_type)
    mqtt.set_humidity_setpoint(package_id, setpoints[0])
    mqtt.set_motion_setpoint(package_id, setpoints[1])
    mqtt.set_temperature_setpoint(package_id, setpoints[2])

