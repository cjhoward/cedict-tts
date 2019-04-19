import os.path
import sys
from aip import AipSpeech

APP_ID = sys.argv[1]
API_KEY = sys.argv[2]
SECRET_KEY = sys.argv[3]

def is_chinese(c):
	return (c >= u'\u4e00' and c < u'\u9fff')

# Build a list of word + pinyin
words = []
with open ('cedict_ts.u8') as file:
	for line in file:
		# Skip comment lines
		if line[0] == '#':
			continue
		
		# Extract word
		word = line.split(' ', 1)[0]

		# Extract pinyin
		pinyin = line[line.find('[')+1:line.find(']')]
		
		# Standardize pinyin
		pinyin = pinyin.lower()
		pinyin = pinyin.replace('u:', 'v')
		pinyin = pinyin.replace('r5', 'er5')

		# Split pinyin into syllables
		syllables = pinyin.split(' ')

		# Ensure one pinyin syllable for each character
		if len(syllables) != len(word):
			continue
		
		# Apply obligatory tone changes
		# https://www.hackingchinese.com/optional-obligatory-tone-change-rules-mandarin/
		pinyin = ''
		for i in range(len(word)):
			# Get current character
			character = word[i]

			# Get corresponding pinyin syllable
			syllable = syllables[i]

			# Skip non-chinese characters
			if not is_chinese(character):
				continue
			
			# Extract tone number
			tone = int(syllable[-1])

			# Get tone of next syllable
			next_tone = 0
			if i + 1 < len(syllables):
				if is_chinese(word[i + 1]):
					next_tone = int(syllables[i + 1][-1])

			if next_tone != 0:
				# If 一 or 不
				if character == u'\u4e00' or character == u'\u4e0d':
					# When it comes before a fourth tone, it’s pronounced as a second tone
					if next_tone == 4:
						tone = 2
					elif next_tone != 5:
						tone = 4
				#else:
				#	if tone == 3 and next_tone == 3:
				#		tone = 2
			# Append tone-correct pinyin syllable to new pinyin string
			pinyin += syllable[:-1] + str(tone)
			if i + 1 < len(syllables):
				pinyin += ' '

		if len(pinyin) == 0:
			continue

		# Append word and pinyin to the list
		words.append({word, pinyin})

# Init Baidu speech client
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
speed = 5 # 0-15, default is 5
pitch = 5 # 0-15, default is 5
volume = 5 # 0-15, default is 5
person = 1 # 0 = female, 1 = male
encoding = 3 # 3 = mp3, 4 = pcm-16k, 5 = pcm-8k, 6=wav

folder = 'output'

for word, pinyin in words:
	# Split pinyin into syllables
	syllables = pinyin.split(' ')

	# Ensure one pinyin syllable for each character
	if len(syllables) != len(word):
		continue

	# Create output filename
	filename = folder + '/' + pinyin.replace(' ', '').replace(',', '-').replace('·', '-') + '.mp3'

	# Skip if file already exsis
	if os.path.isfile(filename):
		continue
	
	# Form speech script
	script = ''
	for i in range(len(word)):
		if syllables[i] == ',' or syllables[i] == '·':
			script += ','
		else:
			if is_chinese(word[i]):
				script += word[i] + '(' + syllables[i] + ')'
			else:
				script += word[i]

	# Perform TTS
	while True:
		try:
			result = client.synthesis(script, 'zh', 1, { 'spd': speed, 'pit': pitch, 'vol': volume, 'per': person, 'aue': encoding })
			if not isinstance(result, dict) and len(result) != 324:
				with open(filename, 'wb') as file:
					file.write(result)
					print('"' + script + '": ' + filename)
			else:
				print('Failed to perform TTS for "' + script + '"')
			break
		except:
			client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
			continue

