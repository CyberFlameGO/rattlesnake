import sys
import pyaudio
import numpy as np


def get_microphone_device_id():
    the_channel_id = None
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        name = str(device.get("name")).lower()
        index = int(str(device.get("index")))
        if "microphone" in name:
            the_channel_id = i
            break
    return the_channel_id


def print_all_devices():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        print(
            (device["index"], device["name"]),
            "\t", ("max input/output channels",device["maxInputChannels"],device["maxOutputChannels"]),
            "\t", ("default_sample_rate", device["defaultSampleRate"])
        )


# PyAudio object variable
pa = pyaudio.PyAudio()

# Size of each read-in chunk
CHUNK = 1
# Amount of channels of the live recording
CHANNELS = 2
# Sample width of the live recording
WIDTH = 2
# Sample rate in Hz of the live recording
SAMPLE_RATE = 44100
# Determines the ratio of the mix
ratio = 1.0


def invert(input_data: bytes):
    """
    Inverts the byte data it received utilizing an XOR operation.

    :param data: A chunk of byte data
    :return inverted: The same size of chunked data inverted bitwise
    """
    data = np.frombuffer(input_data, dtype=np.int16)
    # Invert the integer
    result = np.invert(data)
    # Return the inverted audio data
    return result


def live_mode():
    global ratio

    # Select devices
    print_all_devices()
    print()
    input_device_id = int(input("The input device ID is? __"))
    output_device_id = int(input("The output device ID is? __"))

    # Start live recording
    print('Noise-cancelling is working now...')
    print("Press the ctrl+c to quit.")

    # Create a new PyAudio object using the preset constants
    input_stream = pa.open(
        input_device_index=input_device_id,
        format=pa.get_format_from_width(WIDTH),
        channels= 1,
        rate=SAMPLE_RATE,
        frames_per_buffer=CHUNK,
        input=True,
        output=False,
        # stream_callback = input_callback # type: ignore
     )

    output_stream = pa.open(
        output_device_index=output_device_id,
        format=pa.get_format_from_width(WIDTH),
        channels= 1,
        rate=SAMPLE_RATE,
        frames_per_buffer=CHUNK,
        input=False,
        output=True,
    )

    # Grab a chunk of data in iterations according to the preset constants
    try:
        while True:
            # Read in a chunk of live audio on each iteration
            original = input_stream.read(CHUNK, exception_on_overflow=False)

            # Invert the original audio
            inverted = invert(original)

            # Play back the inverted audio
            output_stream.write(inverted.tobytes(), CHUNK)

    except (KeyboardInterrupt, SystemExit):
        # Terminate the program
        input_stream.stop_stream()
        input_stream.close()

        output_stream.stop_stream()
        output_stream.close()

        pa.terminate()
        sys.exit()