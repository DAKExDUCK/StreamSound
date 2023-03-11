from enum import Enum
from typing import Optional, Union


class Sites(Enum):
    Spotify = "Spotify"
    Spotify_Playlist = "Spotify Playlist"
    YouTube = "YouTube"
    Yandex = "Yandex"
    Yandex_Playlist = "Yandex Playlist"
    Yandex_Album = "Yandex Album"
    Twitter = "Twitter"
    SoundCloud = "SoundCloud"
    Bandcamp = "Bandcamp"
    Custom = "Custom"
    Unknown = "Unknown"


class Playlist_Types(Enum):
    Spotify_Playlist = "Spotify Playlist"
    Yandex_Playlist = "Yandex Playlist"
    Yandex_Album = "Yandex Album"
    YouTube_Playlist = "YouTube Playlist"
    BandCamp_Playlist = "BandCamp Playlist"
    Unknown = "Unknown"


class Origins(Enum):
    Default = "Default"
    Playlist = "Playlist"


def identify_url(url: Optional[str]) -> Sites:
    if url is None:
        return Sites.Unknown

    if "https://www.youtu" in url or "https://youtu.be" in url:
        return Sites.YouTube

    if "https://open.spotify.com/track" in url:
        return Sites.Spotify

    if (
        "https://open.spotify.com/playlist" in url
        or "https://open.spotify.com/album" in url
    ):
        return Sites.Spotify_Playlist
    
    if (
        "https://music.yandex" in url and 
        "album" in url and 
        "/track/" in url
    ):
        return Sites.Yandex

    if (
        "https://music.yandex" in url and 
        "album" in url and 
        not "/track/" in url
    ):
        return Sites.Yandex_Album

    if (
        "https://music.yandex" in url and
        "user" in url and
        "playlists" in url
    ):
        return Sites.Yandex_Playlist

    if "bandcamp.com/track/" in url:
        return Sites.Bandcamp

    if "https://twitter.com/" in url:
        return Sites.Twitter


    if "soundcloud.com/" in url:
        return Sites.SoundCloud

    # If no match
    return Sites.Unknown


def identify_playlist(url: Optional[str]) -> Union[Sites, Playlist_Types]:
    if url is None:
        return Sites.Unknown

    if "playlist?list=" in url:
        return Playlist_Types.YouTube_Playlist

    if (
        "https://open.spotify.com/playlist" in url
        or "https://open.spotify.com/album" in url
    ):
        return Playlist_Types.Spotify_Playlist

    if (
        "https://music.yandex" in url and
        "album" in url and
        not "/track/" in url
    ):
        return Playlist_Types.Yandex_Album

    if (
        "https://music.yandex" in url and
        "user" in url and
        "playlists" in url
    ):
        return Playlist_Types.Yandex_Playlist

    if "bandcamp.com/album/" in url:
        return Playlist_Types.BandCamp_Playlist

    return Playlist_Types.Unknown