i don't know how to write a nice readme so this is me waffling

you'll need selenium for this, so you'll probably have to do a `pip install selenium` somewhere or other, idk. oh yeah also it opens a window in edge (chromium, etc. idk) to do the downloads so idk what'll happen if you're not on windows or if you don't have edge.

ideally you should keep your modlist txt in the same directory as the python script since that's the way i wrote it

```
usage: download.py [-h] [-ml {fabric,forge,quilt,neoforge}] filename ver

Downloads a list of Minecraft mods from Modrinth from a given .txt

positional arguments:
  filename              .txt file with one Modrinth link per line, commented lines should be preceded with '#'
  ver                   minecraft version

options:
  -h, --help            show this help message and exit
  -ml, --modloader {fabric,forge,quilt,neoforge}
                        modloader
```


so yeah your modlist is allowed to have commented lines. only official releases are allowed, so no betas or pre-releases or release candidates or snapshots or anything. the modloader defaults to fabric but it technically supports other loaders (i didn't test this but it should work since there's not really any difference in the download process)

oh yeah and this likely won't work with anything that's not a mod on modrinth, so don't try it bc i don't know what'll happen


you can use the .bat to make it easier since it like, guides you along with it. i was too lazy to learn how to make an .exe so i just wrote a .bat to run the python file isntead.
