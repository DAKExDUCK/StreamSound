import asyncio
import io

import aiohttp
import numpy as np
import sounddevice as sd
from aiohttp import web
from pydub import AudioSegment

from modules.yandex_m_client import YandexMusicClient


CHUNK_SIZE = 1024
SAMPLE_RATE = 44100
CHANNELS = 2


class Room:
    def __init__(self, user):
        self.user = user
        self.songs_queue = []
        self.current_song = None
        self.stream = None
        self.current_audio_seg = None

    async def get_stream(self):
        self.stream = sd.RawOutputStream(samplerate=self.current_audio_seg.frame_rate,
                                        blocksize=CHUNK_SIZE,
                                        channels=self.current_audio_seg.channels,
                                        dtype='int16',
                                        device=None)
        self.stream.start()
        samples = self.current_audio_seg.get_array_of_samples()

        index = 0
        while index < len(samples):
            chunk = samples[index:index + CHUNK_SIZE]
            index += CHUNK_SIZE
            data = np.array(chunk, dtype=np.int16).tobytes()
            self.stream.write(data)
            await asyncio.sleep(0)
        self.stream.stop()
        self.stream.close()
        
        return web.StreamResponse()

    async def add_song(self, url):
        self.songs_queue.append(url)
        if not self.current_song:
            await self.play_next_song()

    async def add_songs(self, urls):
        self.songs_queue.extend(urls)
        if not self.current_song:
            await self.play_next_song()

    async def play_next_song(self):
        if self.songs_queue:
            self.current_song = self.songs_queue.pop(0)

            track = await YandexMusicClient.get_track(self.current_song)
            if not track.available:
                self.next_song()

            await track.get_download_info_async()

            link = [ await info.get_direct_link_async() for info in track.download_info if info.codec == 'mp3' and info.bitrate_in_kbps == 192 ][0]
    
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    if resp.status != 200:
                        return web.Response(text='Error: Unable to download audio file', status=resp.status)
                    data = await resp.read()

            # Stream the audio file to the client
            audio_file = io.BytesIO(data)
            self.current_audio_seg = AudioSegment.from_file(audio_file, format='mp3')
            return await self.get_stream()
        else:
            await self.stop_song()

    async def stop_song(self):
        self.stream.stop()
        self.current_song = None
        self.songs_queue = []

    async def stop_full(self):
        await self.stop_song()
        if self.stream:
            await self.stream.stop()
            await self.stream.close()
            self.stream = None

    async def next_song(self):
        await self.stop_song()
        await self.play_next_song()

    async def prev_song(self):
        if len(self.songs_queue) > 0:
            prev_song = self.current_song
            self.current_song = self.songs_queue.pop()
            self.songs_queue.insert(0, prev_song)
            await self.stop_song()
            await self.play_next_song()
        else:
            # No previous songs in the queue, just replay the current song
            await self.stop_song()
            await self.play_next_song()

rooms: dict[str, Room]= {}
