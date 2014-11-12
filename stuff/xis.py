import struct

# Provides a straightforward means for examining
# sample packets received over the network
class XBeeIOSample:
    
    # Mapping between names and bit-indeces
    DIGITAL_IO_MAP = {
                'AD0': 0,
                'DIO0': 0,
                'AD1': 1,
                'DIO1': 1,
                'AD2': 2,
                'DIO2': 2,
                'AD3': 3,
                'DIO3': 3,
                'DIO4': 4,
                'ASSOC': 5,
                'DIO5': 5,
                'CTS': 7,
                'GPIO7': 7,
                'DIO10': 10,
                'DIO11': 11,
                'CD': 12,
                'DIO12': 12,
             }

    # Mapping between names and bit-indeces
    ANALOG_IO_MAP = {
                'AD0': 0,
                'DIO0': 0,
                'AD1': 1,
                'DIO1': 1,
                'AD2': 2,
                'DIO2': 2,
                'AD3': 3,
                'SUPPLY': 7,
             }

    # Creates a new sample wrapper for the given packet
    def __init__(self, raw_packet):

        # Unpack numerical values from the packet
        sample_sets = struct.unpack('B', raw_packet[0])[0]
        digital_mask = struct.unpack('!H', raw_packet[1:3])[0]
        analog_mask = struct.unpack('B', raw_packet[3])[0]

        # Verify that the sample set value is 1
        if sample_sets != 0x1:
            raise AttributeError, \
                "I/O sample sets field != 1, unable to parse."

        # Create lists of sufficient size to contain all
        # digital and analog values
        max_digital_io = max(self.DIGITAL_IO_MAP.values()) + 1
        max_analog_io = max(self.ANALOG_IO_MAP.values()) + 1
        self.digital_io_state = list( (None,) * max_digital_io )
        self.analog_io_state = list( (None,) * max_analog_io )

        # Begin parsing the variable-length data starting at index
        # 4 which contains the IO state information
        packet_idx = 4
        
        if digital_mask != 0:
            digital_values = struct.unpack('!H',
                             raw_packet[packet_idx:packet_idx+2])[0]

            # Read each bit from the unpacked value
            for bit in range(max_digital_io):
                if (0x1 << bit & digital_mask):
                    self.digital_io_state[bit] = bool((0x1 << bit) & digital_values)
            packet_idx += 2

        for bit in range(max_analog_io):
            if (0x1 << bit) & analog_mask:
                analog_sample = struct.unpack('!H',
                                raw_packet[packet_idx:packet_idx+2])[0]
                # Perform voltage conversion
                self.analog_io_state[bit] = (analog_sample * 1.215) / 1024.0
                packet_idx += 2

    def get_analog_pin(self, name):
        idx = self.ANALOG_IO_MAP[name]
        return self.analog_io_state[idx]

    def get_digital_pin(self, name):
        idx = self.DIGITAL_IO_MAP[name]
        return self.digital_io_state[idx]

    def get_digital_pins(self, *names):
        return map(lambda x: self.get_digital_pin(x), names)

    def get_analog_pins(self, *names):
        return map(lambda x: self.get_analog_pin(x), names)

