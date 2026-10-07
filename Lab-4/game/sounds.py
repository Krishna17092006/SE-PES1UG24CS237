import array
import math

import pygame


class Sounds:
    """Small synthesized sound effects, so no audio files are needed.

    If no audio device is available, every play call is a silent no-op.
    """

    def __init__(self):
        self.enabled = False
        self._sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            self.rate, _, self.channels = pygame.mixer.get_init()
            self.enabled = True
        except pygame.error:
            return

        self._sounds = {
            "brick": self._tone([880], 0.07, 0.35),
            "paddle": self._tone([440], 0.06, 0.35),
            "wall": self._tone([300], 0.04, 0.2),
            "lose_life": self._tone([220, 165], 0.18, 0.35),
            "win": self._tone([523, 659, 784, 1047], 0.13, 0.4),
            "game_over": self._tone([392, 330, 262, 196], 0.18, 0.4),
        }

    def _tone(self, freqs, note_len, volume):
        """Square-wave notes played one after another, with a short fade-out."""
        samples = array.array("h")
        n = int(self.rate * note_len)
        amp = int(32767 * volume)
        for freq in freqs:
            period = self.rate / freq
            for i in range(n):
                fade = 1 - i / n
                value = amp if (i % period) < period / 2 else -amp
                sample = int(value * fade)
                for _ in range(self.channels):
                    samples.append(sample)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        if self.enabled and name in self._sounds:
            self._sounds[name].play()
