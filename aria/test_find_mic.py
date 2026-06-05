import os
import sys

def find_mic():
    try:
        import pyaudio
        old = sys.stderr
        sys.stderr = open(os.devnull, "w")
        pa = pyaudio.PyAudio()
        sys.stderr = old
        mics = []
        for i in range(pa.get_device_count()):
            try:
                info = pa.get_device_info_by_index(i)
                if int(info.get("maxInputChannels", 0)) > 0:
                    mics.append((i, info["name"]))
            except:
                pass
        pa.terminate()
        for i, name in mics:
            if any(k in name.lower() for k in ["bluetooth", "headset", "wireless", "earphone"]):
                return i
        return mics[0][0] if mics else None
    except Exception as e:
        print("Error:", e)
        return None

print("Found mic index:", find_mic())
