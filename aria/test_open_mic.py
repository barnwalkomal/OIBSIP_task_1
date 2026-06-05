import pyaudio

p = pyaudio.PyAudio()
for i in [16, 18, 22, 26, 29, 0, 1]:
    try:
        info = p.get_device_info_by_index(i)
        stream = p.open(input=True, input_device_index=i, rate=16000, channels=1, format=pyaudio.paInt16)
        stream.close()
        print(f"Device {i} ({info['name']}): SUCCESS")
    except Exception as e:
        print(f"Device {i}: FAILED - {e}")
p.terminate()
