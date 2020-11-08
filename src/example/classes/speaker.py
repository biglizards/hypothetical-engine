import openal
from openal import oalOpen

import enginelib.level.save as save
from enginelib import script
from enginelib.game import Entity, savable_args

save.handlers[openal.Source] = lambda source: source.path

# hack to allow setting attribute to trigger setters
is_recursing = False


def __setattr__(self, name, value):
    global is_recursing
    setter = getattr(self, 'set_' + name, None)
    if setter and not is_recursing:
        is_recursing = True
        setter(value)
        is_recursing = False
    else:
        object.__setattr__(self, name, value)


openal.Source.__setattr__ = __setattr__
openal.Source.property_blacklist = ['position', 'velocity', 'source_type', 'path']
# end of hack


class Speaker(Entity):
    def __init__(self, *args, audio_sources=None, play_on_start=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_sources = {}  # {name: source}
        self.play_on_start = play_on_start

        if audio_sources is not None:  # audio sources is {name: path}
            for name, path in audio_sources.items():
                source = oalOpen(path)
                source.path = path
                self.audio_sources[name] = source
            # manually update source vars
            self.update_source_vars.func(self)

        self.savable_attributes.update(savable_args('audio_sources', 'play_on_start'))
        self.property_blacklist.extend(['audio_sources'])

        self.game.add_callback('on_game_start', self.on_game_start)
        self.game.add_callback('on_mode_change', lambda _: self.pause_audio(), always_fire=True)

    @property
    def audio_source(self):
        if len(self.audio_sources) == 1:
            return next(iter(self.audio_sources.values()))
        elif len(self.audio_sources) > 1:
            raise AttributeError(f'Source has {len(self.audio_sources)} sources, not 1 -- ambiguous')
        return None  # if no sources are set

    def add_audio(self, path, name):
        source = oalOpen(path)
        source.path = path
        self.audio_sources[name] = source

    def remove_audio(self, name):
        source = self.audio_sources[name]
        source.stop()
        del self.audio_sources[name]

    @script.every_n_ms(1000)
    def update_source_vars(self, _delta_t=0):
        source: openal.Source
        for source in self.audio_sources.values():
            source.set_position(self.position)
            source.set_velocity(self.velocity)

    def play_audio(self, name=None):
        if not self.audio_sources:
            raise RuntimeError("this entity has no sources")
        if name is None and self.audio_source is None:
            raise RuntimeError(f"'name' was omitted, but this entity has multiple sources")
        self.audio_source.play()

    def stop_audio(self):
        for source in self.audio_sources.values():
            source.stop()

    def pause_audio(self):
        for source in self.audio_sources.values():
            source.pause()

    def remove(self):
        self.super(Speaker).remove()
        self.game.remove_callback('on_game_start', self.on_game_start)
        self.stop_audio()

    def on_game_start(self):
        if self.play_on_start:
            self.play_audio()
