# play-sound.pydub
from pydub import AudioSegment
from pydub.playback import play

song = AudioSegment.from_wav("bell-notif.wav")
print('playing sound using  pydub')
play(song)
