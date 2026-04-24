import pygame
import numpy as np
import os

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            # Base sounds
            self.sounds = {
                "laser": self._generate_laser_sound(),
                "explosion": self._generate_explosion_sound(),
                "hit": self._generate_hit_sound(),
                "game_over": self._generate_game_over_sound(),
                "powerup": self._generate_powerup_sound(),
                "rocket": self._generate_rocket_sound(),
                "intro": self._generate_intro_sound(),
            }
            
            # Try load wavs
            sound_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sounds')
            shoot_path = os.path.join(sound_dir, 'shoot.wav')
            if os.path.exists(shoot_path):
                self.sounds["laser"] = pygame.mixer.Sound(shoot_path)
                self.sounds["laser"].set_volume(0.2)
                
            exp_path = os.path.join(sound_dir, 'explosion.wav')
            if os.path.exists(exp_path):
                self.sounds["explosion"] = pygame.mixer.Sound(exp_path)
                self.sounds["explosion"].set_volume(0.3)
                
            print("Status: Audio Manager Initialized.")
        except Exception as e:
            print(f"Status: Audio Init Failed ({e})")
            self.sounds = {}

    def _generate_laser_sound(self):
        duration = 0.15
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(1200, 300, len(t))
        wave = np.sin(2 * np.pi * freq * t)
        wave *= np.exp(-12 * t)
        return self._create_sound(wave)

    def _generate_rocket_sound(self):
        duration = 0.4
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(200, 50, len(t))
        wave = np.sin(2 * np.pi * freq * t)
        noise = np.random.uniform(-0.5, 0.5, len(t)) * np.exp(-5 * t)
        wave = (wave + noise) * np.exp(-2 * t)
        return self._create_sound(wave)

    def _generate_explosion_sound(self):
        duration = 0.3
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.random.uniform(-1, 1, len(t))
        wave = np.convolve(wave, np.ones(10)/10, mode='same')
        wave *= np.exp(-8 * t)
        return self._create_sound(wave)

    def _generate_hit_sound(self):
        duration = 0.15
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(150, 50, len(t))
        tone = np.sin(2 * np.pi * freq * t)
        noise = np.random.uniform(-1, 1, len(t))
        wave = tone * 0.4 + noise * 0.6
        wave *= np.exp(-15 * t)
        return self._create_sound(wave)
        
    def _generate_powerup_sound(self):
        duration = 0.3
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.zeros_like(t)
        n = len(t)
        freq[:n//3] = 440
        freq[n//3:2*n//3] = 554 
        freq[2*n//3:] = 659
        wave = np.sin(2 * np.pi * freq * t)
        wave *= np.exp(-5 * t)
        return self._create_sound(wave)

    def _generate_game_over_sound(self):
        duration = 1.0
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(400, 100, len(t))
        wave = np.sin(2 * np.pi * freq * t)
        wave *= np.exp(-3 * t)
        return self._create_sound(wave)

    def _generate_intro_sound(self):
        duration = 22.0 # Longer duration to cover the whole intro (Logo + Story + Hyperspace)
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Track 1: Deep Space Drone (C2 ~ 65.41 Hz)
        bass_freq = 65.41
        bass = 0.4 * np.sin(2 * np.pi * bass_freq * t) + 0.1 * np.sin(2 * np.pi * bass_freq * 2 * t)
        
        # Track 2: Mysterious Arpeggio (C minor: C4, Eb4, G4, C5)
        arp_freqs = [261.63, 311.13, 392.00, 523.25]
        arp = np.zeros_like(t)
        note_duration = 0.25 # Speed of arpeggio
        for i in range(int(duration / note_duration)):
            start_idx = int(i * note_duration * sample_rate)
            end_idx = int((i + 1) * note_duration * sample_rate)
            if end_idx > len(t): end_idx = len(t)
            f = arp_freqs[i % len(arp_freqs)]
            t_note = t[start_idx:end_idx] - t[start_idx]
            # Pluck envelope for arpeggio
            env = np.exp(-4 * t_note)
            arp[start_idx:end_idx] = 0.2 * np.sin(2 * np.pi * f * t_note) * env
            
        # Track 3: Sweeping Pad (Space vibe)
        pad_freq = 130.81 # C3
        lfo = np.sin(2 * np.pi * 0.1 * t) # Very slow LFO for pitch modulation
        pad = 0.15 * np.sin(2 * np.pi * (pad_freq + 5 * lfo) * t)
        
        # Mix tracks
        wave = bass + arp + pad
        
        # Master Envelope (Smooth fade in and out)
        envelope = np.ones_like(t)
        fade_in_samples = int(sample_rate * 3.0) # 3 seconds fade in
        fade_out_samples = int(sample_rate * 2.0) # 2 seconds fade out
        envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
        envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)
        wave *= envelope
        
        return self._create_sound(wave)

    def _create_sound(self, wave):
        wave = np.clip(wave, -1.0, 1.0)
        audio_data = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio_data, audio_data))
        stereo = np.ascontiguousarray(stereo)
        return pygame.mixer.Sound(buffer=stereo)

    def play(self, name, volume=1.0):
        if name in self.sounds:
            snd = self.sounds[name]
            # If using wav files, volume might be preset, let's just use the param if possible
            snd.set_volume(volume)
            snd.play()

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()
            
    def fadeout(self, name, time_ms=1000):
        if name in self.sounds:
            self.sounds[name].fadeout(time_ms)
