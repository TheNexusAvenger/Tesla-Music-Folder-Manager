# Tesla Music Folder Manager
Teslas have the ability to play audio files from USB
drives, but the user interface is very basic with
no ways to manage sorting (at least of release 
2020.44 / V.10.2). This project exploits the ordering
used by Tesla presented in the folder view to use the
folder view for artists with tracks grouped properly
by album and in descending order of year.

### Why Not Stream?
Streaming is problematic for drives where an LTE
connection is not guaranteed, or you listen to specific
songs that aren't available on services like Spotify,
such as unofficial remixes that can't be on due to legal
problems.

### Why Not Bluetooth?
On Android, the volume is shared between devices, meaning
you need to constantly switch between full volume and a
proper listening volume. Bluetooth also uses more battery
life and can be less reliable than USB.

## Setup
### Music
For music, it works by having a source directory of music
files with the year, album name, artist, and track number
metadata specified, and a target directory like a USB drive.

### Script
The scripts require Python 3 to run with the requirements
in `requirements.txt` used. Setup can be used with the following:
```
pip install requirements.txt
```

### Running
A configuration file named `configuration.json` is required. It
can contain:
- `sourceDirectory` (required): Directory to copy from.
- `targetDirectory` (required): Directory to copy to.
- `extensionsWhitelist` (optional): Optional list of file extensions to allow. By default, any file is allowed.
- `fileWhitelist` (optional): Optional list of allowed file paths. Regular expressions are supported.
- `fileBlacklist` (optional): Optional list of not allowed file paths. Regular expressions are supported.

Below is an example configuration to copy from `C:\Users\User\Music`
to `D:` for only `mp3` and `m4a` files.

```json
{
  "sourceDirectory": "C:/Users/User/Music",
  "targetDirectory": "D:",
  "extensionsWhitelist": ["mp3", "m4a"]
}
```

Below is an example configuration for only the directories
`Artist1` and `Artist2`, excluding `Artist1/Album1`.

```json
{
  "sourceDirectory": "C:/Users/User/Music",
  "targetDirectory": "D:",
  "extensionsWhitelist": ["mp3", "m4a"],
  "fileWhitelist": [
    "Artist1",
    "Artist2"
  ],
  "fileBlacklist": [
    "Artist1/Album1"
  ]
}
```

Running the script can be done with the following:
```
python TeslaFormatWriter.py
```

## Method
The files in the source directory are indexed, with tracks being
split by artist. After this, a directory is made for each artist
with the tracks copied over. What is different, and why this script
should be used, is how the file names are modified. To ensure the
order, an increment for the year, the album name, and the track name
are used.

### Identifier Format
Consider the following tracks:
* Artist 1
    * Album1 (2018)
        * 1 Track1
        * 5 Track2
        * 12 Track3
    * Album2 (2020)
        * 2 Track1
        * 3 Track2
* Artist 2
    * Album1 (2019)
        * 1 Track1
    * 1 SomeSingle (2019)

For each file, the following will be added to the front:
`YearIncrementer_AlbumName_TrackId`
* YearIncrementer - Incrementer for years, starting at 1 for the latest album and increasing by 1 for each year from the newest album.
* AlbumName - The album name, which is used if the years are the same.
* TrackId - The track id of the album, which is used if the album names are the same.

When needed, leading zeros are added since Tesla compares the individual
characters instead of the numbers. For example, comparing 2, 4, and 13 would
start result in comparing only 2, 4, and 1, leading to the order being 13, 2, 4.
With 02, 04, and 13, the comparison becomes 0, 0, and 0, and then 2 and 4, leading
to the correct order 02, 04, and 13. For the example tracks above, the structure
would be created in the destination directory:
* Artist 1
    * 1_Album2_2Track1
    * 1_Album2_3Track2
    * 3_Album1_01Track1
    * 3_Album1_05Track2
    * 3_Album1_12Track3
* Artist 2
    * 1_Album1_1Track1
    * 1_SomeSingle_1SomeSingle

After the files are written, files that are in the destination directory
that weren't written will be cleaned up. This is intended for music librar
changes, such as removing songs or replacing singles when they get re-released
as albums.

#### Limitation - Year Incrementer
The year incrementer is used because the years need to increment
to start at the latest, and the latest album + 1 is used as the
zero point. If the latest album's year changes, this will result
in the entire artist being re-copied.

If you are looking at the files and see 8 digits used instead
of 4 for the incrementer, the file that starts in 00000001 most
likely has 2 year metadata tags.

### Re-Running
This project is intended to be re-run as the source music
library changes with time. If a file hasn't changed, like the
contents or metadata, it will not be re-copied. The time spent
indexing will be the same with re-runs, but copying files will
only be long for the first time and major changes to the source
music library.

### Long-Term Use
This script was written at the time of release 2020.44 (v.10.2).
The interface for USB changed a lot since the earlier versions in
v.8, and most likely will change in the future. This probably will
not be needed in the future; either by a better USB player or the USB
player being removed.