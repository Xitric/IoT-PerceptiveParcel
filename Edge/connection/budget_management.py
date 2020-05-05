import utime

class Message:
    """
    A struct of information related to an interesting sample. Contains the
    following values:
    - `time`: The time when the sample was made
    - `value`: The measurement value
    - `delta`: How much the measurement exceeds setpoint values
    """

    def __init__(self, topic: str, time: float, value: float, delta: float):
        self.topic = topic
        self.time = time
        self.value = value
        self.delta = delta

    def __str__(self):
        return 'Message[tp={},t={},v={},d={}]'.format(self.topic, self.time, self.value, self.delta)


class MessageBuffer:
    """
    A buffer of messages to be sent in batch. This allows for a better
    utilization of the available budget by not sending half-filled packets.
    Furthermore, it prioritizes the most important messages. Thus, if a buffer
    can hold two messages, but three messages are appended, the least
    significant message is dropped.
    """

    def __init__(self, size: int):
        self.size = size
        self.stack = []

    def push_message(self, topic: str, time: float, value: float, delta: float):
        message = Message(topic, time, value, delta)

        for index, msg in enumerate(self.stack):
            if msg.delta < delta:
                self.__shift_messages(index)
                self.stack[index] = message
                return

        if len(self.stack) < self.size:
            self.stack.append(message)

    def __shift_messages(self, from_index: int):
        for index in range(len(self.stack), from_index, -1):
            if index < self.size:
                self.__put(index, self.stack[index - 1])

    def __put(self, index: int, message: Message):
        if index >= self.size:
            raise IndexError('buffer index out of range')

        while len(self.stack) <= index:
            self.stack.append(None)

        self.stack[index] = message

    def extract_messages(self) -> [Message]:
        """Extracts all messages from the buffer and sorts them by time."""

        result = self.stack[:]
        result.sort(key=lambda msg: msg.time)
        self.stack.clear()
        return result


class Budget:
    """Used to keep track of the remaining transmission budget."""

    def __init__(self, daily_transmits: int, replenish_delay: int, packet_size: int, message_size: int):
        self.remaining_transmits = daily_transmits
        self.period_length = replenish_delay
        self.packet_capacity = packet_size // message_size  # Floor division
        self.recommended_transmit_interval = replenish_delay // daily_transmits

    def use_transmit(self):
        if self.remaining_transmits == 0:
            raise RuntimeError('no remaining transmits')
        self.remaining_transmits -= 1

    def has_exceeded_transmit_interval(self, time: float):
        if self.remaining_transmits == 0:
            return False

        remaining_time = self.period_length - time % self.period_length
        return remaining_time // self.remaining_transmits < self.recommended_transmit_interval


class TransmissionModel:
    """Used to evaluate if it is worth sending a message."""

    def __init__(self, significant_delta: float, early_transmit_factor: float):
        self.significant_delta = significant_delta
        self.early_transmit_factor = early_transmit_factor

    def should_transmit(self, time: float, buffer: MessageBuffer, budget: Budget) -> bool:
        # Never transmit an empty buffer, duh
        if len(buffer.stack) == 0:
            return False
        
        if len(buffer.stack) == buffer.size:
            if budget.has_exceeded_transmit_interval(time):
                # Transmit if we have filled the buffer and it is time to transmit
                return True
            else:
                # Transmit early only if all messages are significant
                return buffer.stack[buffer.size - 1].delta > self.significant_delta
        else:
            # Transmit a partial buffer only if the message is very significant
            return buffer.stack[0].delta > self.significant_delta * self.early_transmit_factor


# A simulation using adaptive sampling and batch transmissions
class BudgetManager:
    """Used to manage when a message is sent over a network connection."""

    def __init__(self, budget: Budget, transmission_model: TransmissionModel):
        self.start_time = utime.time()
        self.simulation_end = budget.period_length
        self.budget = budget
        self.model = transmission_model
        self.buffer = MessageBuffer(budget.packet_capacity)

    def enqueue(self, topic: str, time: float, value: float, setpoint: float):
        self.buffer.push_message(topic, time, value, (value - setpoint) / setpoint)
    
    # Run in messaging service or something
    def should_transmit(self):
        time = utime.time() - self.start_time
        if time > 1000000000:
            # Would seem as if the NTP service has updated the clock
            self.start_time = utime.time()
            time = utime.time() - self.start_time
        
        return self.model.should_transmit(time / 60, self.buffer, self.budget)

    # Run in MQTT service when tasked to send messages
    # Store in out buffer until network is available
    # So, instead of writing directly to out buffer, we first write to the
    # budget manager, and then to the out buffer later
    def get_transmission_package(self):
        self.budget.use_transmit()
        return self.buffer.extract_messages()
