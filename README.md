# CEDICT TTS

This repository contains Baidu Speech-generated TTS MP3s for all entries in the CC-CEDICT Chinese-English dictionary, as well as the Python script and dictionary file used to generate them. The `female` and `male` directories contain the generated MP3s in female (0) and male (1) voices, respectively. All MP3s were generated using the default speed (5), pitch (5), and volume (5). Higher quality audio can be obtained by changing the encoding to WAV and regenerating the audio.

## Audio Usage

All audio files are in lowercase, and are named according to their pinyin pronunciations. The pinyin is numeric (i.e. pin1yin1 not pīnyīn), 'v' is used in place of 'ü', and 'er5' is used rather than 'r5'. Following the above rules, the corresponding MP3 for '律师' would be `lv4shi1.mp3`.

To get the correct pronunciation for words with '一' and '不', ensure that you use the tone-corrected pinyin when obligatory tone change rules apply. For example, the pinyin for '一切' should be 'yi2qie4' rather than 'yi1qie4'.

### Anki

This data is particularly useful when creating Anki flashcards. First, copy all audio files from either the `female` or `male` directory to your Anki media folder. Then, provided that your card has a `pinyin` field, insert the line `[sound:{{pinyin}}.mp3]` to your card template to automatically add pronunciation audio to all cards.

## Script Usage

In order to generate TTS audio using Baidu's speech synthesis service, you must have installed the [Baidu RESTful API Python SDK](http://ai.baidu.com/sdk#asr), and have been issued an API key for the Baidu Speech API. Instructions for this process (in Chinese) can be found [here](http://ai.baidu.com/docs#/ASR-API/top).

After you have been issued an API key, copy down your app ID, API key, and secret key, as these are used as parameters to the TTS script. Finally, the script can be used as follows:

    python3 tts.py <app ID> <API key> <secret key>

This will generate MP3s for all entries in the `cedict_ts.u8` file. Feel free to edit the script manually to change the speed, pitch, volume, person, and encoding parameters as desired. See the [Baidu TTS REST API](http://ai.baidu.com/docs#/TTS-API/top) (Chinese) for more information about the parameters.
