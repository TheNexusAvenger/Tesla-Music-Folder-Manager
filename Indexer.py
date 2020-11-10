"""
TheNexusAvenger

Indexes a directory of music files.
"""

from tinytag import TinyTag,TinyTagException
import eyed3
import os
import re
import sanitize_filename



"""
Cleans a string for use with file names.
"""
def cleanForFileName(string):
    return sanitize_filename.sanitize(string)



"""
Data class for a track.
"""
class Track:
    """
    Creates a track.
    """
    def __init__(self,album,track,year,fileLocation):
        self.album = cleanForFileName(album).strip()
        self.track = track
        self.year = year
        self.fileLocation = fileLocation

    """
    Returns if an object is equal.
    """
    def __eq__(self,obj):
        return isinstance(obj,Track) and obj.album == self.album and obj.track == self.track

"""
Data class for an artist.
"""
class Artist:
    """
    Creates an artist.
    """
    def __init__(self,artistName):
        self.artistName = cleanForFileName(artistName).strip()
        self.tracks = []

    """
    Adds a song to the artist.
    """
    def addSong(self,album,track,year,fileLocation):
        # Return if the song exists.
        track = Track(album,track,year,fileLocation)
        if track in self.tracks:
            return

        # Add the track.
        self.tracks.append(track)

"""
Helper class for indexing files.
"""
class Indexer:
    """
    Creates an indexer.
    """
    def __init__(self):
        self.artists = {}

    """
    Adds a file to the index.
    """
    def indexFile(self,fileLocation):
        # Load the metadata tags and return if some audio tags are missing.
        try:
            metadata = TinyTag.get(fileLocation)
            if metadata.bitrate is None:
                return
        except TinyTagException:
            return

        # Read the metadata using TinyTag.
        artist = metadata.artist
        album = metadata.album
        track = metadata.track
        year = metadata.year

        # Reset the track and year if they aren't integers.
        if track is not None:
            try:
                track = int(track)
            except ValueError:
                track = None
        if year is not None:
            try:
                year = int(year)
            except ValueError:
                # Find the first number. Some files include a timestamp rather than year.
                # The first number is assumed to be the year.
                foundNumbers = re.findall(r'\d+',year)
                if len(foundNumbers) > 0:
                    year = int(foundNumbers[0])
                else:
                    year = None

        # Add missing attributes using eyed3.
        # This is because TinyTag sometimes doesn't fetch some attributes in testing.
        if artist is None or album is None or track is None or year is None:
            backupMetadata = eyed3.load(fileLocation)
            if backupMetadata is not None:
                metadataTags = backupMetadata.tag
                if metadataTags:
                    # Add the missing tags.
                    if artist is None and hasattr(metadataTags,"artist"):
                        artist = metadataTags.artist
                    if album is None and hasattr(metadataTags,"albumName"):
                        album = metadataTags.albumName
                    if track is None and hasattr(metadataTags,"trackNumber"):
                        track = metadataTags.trackNumber
                    if year is None and hasattr(metadataTags,"recording_date") and metadataTags.recording_date is not None:
                        year = int(metadataTags.recording_date.year)

        # Add default tags and parse the tags.
        if artist is None:
            print("\t" + fileLocation + " doesn't have a detected artist name.")
            artist = "Unknown"
        if album is None:
            print("\t" + fileLocation + " doesn't have a detected album name.")
            album = "Unknown"
        if track is None:
            print("\t" + fileLocation + " doesn't have a detected track number.")
            track = 1
        if year is None:
            print("\t" + fileLocation + " doesn't have a detected year.")
            year = 2000

        # Add the indexed track.
        artist = artist.strip()
        if artist.lower() not in self.artists.keys():
            self.artists[artist.lower()] = Artist(artist)
        self.artists[artist.lower()].addSong(album,track,year,fileLocation)

    """
    Indexes a directory.
    """
    def indexDirectory(self,directory):
        directory = directory.replace("/","\\")

        # Add the files and directories.
        for file in os.listdir(directory):
            path = os.path.join(directory,file)
            if os.path.isdir(path):
                # Recursively index the directory.
                self.indexDirectory(path)
            elif os.path.isfile(path):
                # Add the file.
                self.indexFile(path)

    """
    Returns the indexed artists.
    """
    def getArtists(self):
        return self.artists



"""
Returns a table of artists and tracks.
"""
def indexDirectory(directory):
    indexer = Indexer()
    indexer.indexDirectory(directory)
    return indexer.getArtists()