# Development branch for CFDDNSUpdater

I'm planning on rebuilding this from scratch to simplify, increase the ease of usability, and implement missing functionaility.
This is mostly driven by my need to have multiple domains being updated.

Would be nice to allow other sources of fetching the current external IP.
Rely more on self-ping rather than firing off external requests all the time. Hitting your own domain, etc...

Rely more upon a config file as the default as these are often easiest to work with as a novice user, but also allow config porting, etc..

I'm keen to continue the trend of no external module requirements so this can get a grab-and-go approach without needing external requirements.