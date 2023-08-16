'''
Created on 2023-08-16

@author: wf
'''
import pysrt


class SRT:
    """
    Class to represent and manipulate SRT (SubRip Subtitle) data.
    
    Attributes:
        subtitles (list): List of parsed subtitles.
    """

    def __init__(self, subtitles):
        """
        Initializes the SRT object with the given subtitles.

        Args:
            subtitles (list): List of parsed subtitles.
        """
        self.subtitles = subtitles

    @classmethod
    def from_text(cls, text):
        """
        Class method to create an SRT object from a raw text string.

        Args:
            text (str): Raw SRT formatted string.

        Returns:
            SRT: An instance of the SRT class initialized with parsed subtitles.
        """
        subtitles = pysrt.from_string(text)
        return cls(subtitles)

    def extract_value(self, index, key):
        """
        Extracts the value for a given key from the subtitle at the specified index.

        Args:
            index (int): The index of the subtitle from which the value should be extracted.
            key (str): The key for which the value should be extracted.

        Returns:
            str: Extracted value for the given key, or None if key is not found.
        """
        text = self.subtitles[index].text
        try:
            start_index = text.index(f"[{key}:") + len(key) + 2
            end_index = text.index("]", start_index)
            return text[start_index:end_index].strip()
        except ValueError:
            return None
