"""
TheNexusAvenger

Indexes a directory of music files.
"""

import eyed3
import os
import re
import sanitize_filename
from tinytag.tinytag import TinyTag, TinyTagException
from typing import Dict
from Configuration import Configuration


class Track:
    def __init__(self, album: str, title: str, track: str, year: int, fileLocation: str):
        """Creates a track.

        :param album: Name of the album the track is part of.
        :param title: Title of the track.
        :param track: Index of the track.
        :param year: Year of the track.
        :param fileLocation: Location of the track.
        """

        self.album = sanitize_filename.sanitize(album).strip()
        self.title = title
        self.track = track
        self.year = year
        self.fileLocation = fileLocation

    def __eq__(self, obj: object) -> bool:
        """Returns if an object is equal.

        :param obj: Object to compare.
        """
        return isinstance(obj, Track) and obj.album == self.album and obj.track == self.track


class Artist:
    def __init__(self, artistName: str):
        """Creates an artist.

        :param artistName: Name of the artist.
        """

        self.artistName = sanitize_filename.sanitize(artistName).strip()
        self.tracks = []

    def addSong(self, album: str, title: str, track: str, year: int, fileLocation: str) -> None:
        """Adds a track to the artist.

        :param album: Name of the album the track is part of.
        :param title: Title of the track.
        :param track: Index of the track.
        :param year: Year of the track.
        :param fileLocation: Location of the track.
        """

        # Return if the song exists.
        track = Track(album, title, track, year, fileLocation)
        if track in self.tracks:
            return

        # Add the track.
        self.tracks.append(track)


class Indexer:
    def __init__(self, configuration: Configuration):
        """Creates an indexer.

        :param configuration: Configuration for the filter.
        """

        self.configuration = configuration
        self.artists = {}

    def indexFile(self, fileLocation: str) -> None:
        """Adds a file to the index.

        :param fileLocation: File to index.
        """

        # Return if the filter does not pass.
        if not self.configuration.fileAllowed(fileLocation):
            return

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
        title = metadata.title
        track = metadata.track
        year = metadata.year
        if title == "":
            title = None

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
                foundNumbers = re.findall(r'\d+', year)
                if len(foundNumbers) > 0:
                    year = int(foundNumbers[0])
                else:
                    year = None

        # Add missing attributes using eyed3.
        # This is because TinyTag sometimes doesn't fetch some attributes in testing.
        if artist is None or album is None or title is None or track is None or year is None:
            backupMetadata = eyed3.load(fileLocation)
            if backupMetadata is not None:
                metadataTags = backupMetadata.tag
                if metadataTags:
                    # Add the missing tags.
                    if artist is None and hasattr(metadataTags, "artist"):
                        artist = metadataTags.artist
                    if album is None and hasattr(metadataTags, "albumName"):
                        album = metadataTags.albumName
                    if title is None and hasattr(metadataTags, "title"):
                        title = metadataTags.title
                    if track is None and hasattr(metadataTags, "trackNumber"):
                        track = metadataTags.trackNumber
                    if year is None and hasattr(metadataTags, "recording_date") and metadataTags.recording_date is not None:
                        year = int(metadataTags.recording_date.year)

        # Add default tags and parse the tags.
        if artist is None:
            print("\t" + fileLocation + " doesn't have a detected artist name.")
            artist = "Unknown"
        if album is None:
            print("\t" + fileLocation + " doesn't have a detected album name.")
            album = "Unknown"
        if title is None:
            print("\t" + fileLocation + " doesn't have a detected track name.")
            title = "Unknown"
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
        self.artists[artist.lower()].addSong(album, title, track, year, fileLocation)

    def indexDirectory(self, directory: str) -> None:
        """Adds a file to the index.

        :param directory: Directory to index.
        """

        directory = directory.replace("/", "\\")

        # Return if the directory should be ignored.
        if self.configuration.fileBlacklisted(directory):
            return

        # Add the files and directories.
        try:
            for file in os.listdir(directory):
                path = os.path.join(directory, file)
                if os.path.isdir(path):
                    # Recursively index the directory.
                    self.indexDirectory(path)
                elif os.path.isfile(path):
                    # Add the file.
                    self.indexFile(path)
        except PermissionError:
            print("Could not access " + directory + ". Ignoring.")
            pass

    def getArtists(self) -> Dict[str, Artist]:
        """Returns the indexed artists.

        :return: Artists with tracks that were indexed.
        """
        return self.artists


def indexDirectory(configuration: Configuration) -> Dict[str, Artist]:
    """Returns a table of artists and tracks.

    :param configuration: Configuration for the paths and filter.
    :return: Artists with tracks that were indexed.
    """

    indexer = Indexer(configuration)
    for sourceDirectory in configuration.sourceDirectories:
        indexer.indexDirectory(sourceDirectory)
    return indexer.getArtists()
