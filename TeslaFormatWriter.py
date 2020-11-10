"""
TheNexusAvenger

Writes files for the Tesla format.
"""

import Indexer
import math
import ntpath
import os
import shutil
import sys



"""
Class that writes files.
"""
class TeslaFormatWriter:
    """
    Creates the writer.
    """
    def __init__(self,destinationLocation):
        self.destinationLocation = destinationLocation.replace("/","\\")
        self.filesWritten = []

    """
    Writes files to the destination.
    """
    def writeTracks(self,artists):
        # Add the artists and tracks.
        # The keys are sorted so that the artists are done in order by name.
        artistNames = list(artists.keys())
        artistNames.sort()
        for artistName in artistNames:
            # Fetch the artist.
            artist = artists[artistName]

            # Create the directory.
            print("Writing " + artist.artistName)
            artistDirectory = os.path.join(self.destinationLocation,artist.artistName)
            if not os.path.exists(artistDirectory):
                os.mkdir(artistDirectory)

            # Determine the newest year, oldest year, and highest track number.
            newestYear = 0
            oldestYear = sys.maxsize
            highestTrack = 1
            for track in artist.tracks:
                if track.year > newestYear:
                    newestYear = track.year
                if track.year < oldestYear:
                    oldestYear = track.year
                if track.track > highestTrack:
                    highestTrack = track.track

            # Create the identifier format.
            identifierFormat = "{:0" + str(math.floor(math.log10(newestYear - oldestYear + 1) + 1)) + "d}_{:s}_{:0" + str(math.floor(math.log10(highestTrack) + 1)) + "d}"

            # Copy the tracks.
            for track in artist.tracks:
                # Determine the identifier and location.
                identifier = identifierFormat.format(newestYear - track.year + 1,track.album,track.track)
                trackDirectory = os.path.join(artistDirectory,identifier + "_" + ntpath.basename(track.fileLocation))
                self.filesWritten.append(trackDirectory)

                # Copy the file.
                if os.path.isfile(trackDirectory):
                    sourceModifiedTime = os.path.getmtime(track.fileLocation)
                    targetModifiedTime = os.path.getmtime(trackDirectory)
                    sourceFileSize = os.path.getsize(track.fileLocation)
                    targetFileSize = os.path.getsize(trackDirectory)

                    if sourceModifiedTime > targetModifiedTime or sourceFileSize != targetFileSize:
                        shutil.copyfile(track.fileLocation,trackDirectory)
                else:
                    shutil.copyfile(track.fileLocation,trackDirectory)

    """
    Cleans a directory of unintended files.
    """
    def cleanDirectory(self,directory):
        # Clean the files and directory.
        for file in os.listdir(directory):
            path = os.path.join(directory,file)
            if os.path.isdir(path):
                # Clean the subdirectory.
                self.cleanDirectory(path)
            elif os.path.isfile(path):
                # Remove the file if it wasn't written.
                if path not in self.filesWritten:
                    os.remove(path)

        # Delete the directory if it is empty.
        if len(os.listdir(directory)) == 0:
            os.removedirs(directory)

    """
    Cleans the files that weren't written.
    """
    def cleanTracks(self):
        self.cleanDirectory(self.destinationLocation)



"""
Runs the program.
"""
if __name__ == '__main__':
    # Return if the arguments don't exist.
    if len(sys.argv) != 3:
        print("Usage: TeslaFormatWriter.py sourceDirectroy destinationDirectory")
        exit(-1)

    # Add slashes to root drives.
    if sys.argv[1][-1] == ":":
        sys.argv[1] += "\\"
    if sys.argv[2][-1] == ":":
        sys.argv[2] += "\\"

    # Index the files.
    print("Indexing files.")
    artists = Indexer.indexDirectory(sys.argv[1])

    # Write the directories.
    print("Writing files.")
    writer = TeslaFormatWriter(sys.argv[2])
    writer.writeTracks(artists)

    # Clean the directories.
    print("Cleaning directories.")
    writer.cleanTracks()
