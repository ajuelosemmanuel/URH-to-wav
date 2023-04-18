# URH to wav

Script that turns a .complex file from URH (Universal Radio Hacker) to a .wav file

The point of this script is to get "listen-able" audio from a radio recording.

PS : two audio files are created - one has Butterworth filtering and the other hasn't. You can differenciate those by the name (one has "filt" in it).

## Installation

First, make sure to have a recent version of [Python 3](https://www.python.org/downloads/).

Then, install the required packages so the script can run.

Windows :
```bash
py -m pip install -r requirements.txt
```

Linux :
```bash
pip install -r requirements.txt
```

# Usage

```
python urhtowav.py [yourfile.complex]
```

Note : Default values for the sampling frequency and the downer are 1000000 and 7. You can change those at the end of the script.
