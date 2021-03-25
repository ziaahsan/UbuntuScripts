## Installation and Usage

Simply clone this repo and make sure you have all the required dependencies to be included
when using the imports.

```bash
# Simply Clone this repository
git clone https://github.com/ziaahsan/UbuntuScripts.git

# To simply run as background service do:
python3 /home/user/UbuntuScripts/daylight/main.py > /home/user/UbuntuScripts/daylight/log/stdout.txt 2> /home/user/UbuntuScripts/daylight/log/stderr.txt &

# To launch at start up:
# 1. Search startup app
# 2. place the above command in the command section this would ensure application runs
#    on the start of the ubuntu
```
---

Any feedback to improve code is welcome.
This script is very simply and still is in progress.

Todo:
1. Fix the @todo's inside the scripts
2. Make OOP if needed but for now contemplating what I want from this (so far does exactly what I want any suggesstion is more than welcome)
3. Create a requirement.txt

Feature:
1. Changes wallpaper based on time (if automatic)
2. 5 sequence of wallpaper loaded from the screen directory: Dawn, Sun Rise, Noon, Sun Set, Dusk
3. Changes theme (hard coded can be configured) based on 2. Default all set to Yaru-Dark

Future features (thinking about so far):
1. Want to make it like IOS dynamic wallpaper where maybe as the day progress a differnt image frame is shown (Easy but thinking about the battery life,  and other things. Comments are welcome)
2. Maybe include weather in this wallpaper watch somehow
