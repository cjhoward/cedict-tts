import os.path
import sys
from aip import AipSpeech

APP_ID = sys.argv[1]
API_KEY = sys.argv[2]
SECRET_KEY = sys.argv[3]

speed = 5 # 0-15, default is 5
pitch = 5 # 0-15, default is 5
volume = 5 # 0-15, default is 5
person = 1 # 0 = female, 1 = male
encoding = 3 # 3 = mp3, 4 = pcm-16k, 5 = pcm-8k, 6=wav
extension = '.wav'
if encoding == 3:
	extension = '.mp3'
output_directory = 'output'

def is_cjk(c):
	# CJK Unified Ideographs block
	if (c >= u'\u4e00' and c <= u'\u9fff'):
		return True
	# CJKUI Ext A block
	if (c >= u'\u3400' and c <= u'\u4db5'):
		return True
	# CJKUI Ext B block
	if (c >= u'\u20000' and c <= u'\u2a6d6'):
		return True
	# CJKUI Ext C block
	if (c >= u'\u2a700' and c <= u'\u2b734'):
		return True
	# CJKUI Ext D block
	if (c >= u'\u2b740' and c <= u'\u2b81d'):
		return True
	# CJKUI Ext E block
	if (c >= u'\u2b820' and c <= u'\u2ceaf'):
		return True
	# CJKUI Ext F block
	if (c >= u'\u2ceb0' and c <= u'\u2ebef'):
		return True

def standardize_pinyin(pinyin):
	pinyin = pinyin.lower()
	pinyin = pinyin.replace('u:', 'v')
	pinyin = pinyin.replace('r5', 'er5')
	pinyin = pinyin.replace('xx5', 'xx').replace('xx', 'xx5')
	return pinyin

def slugify_pinyin(pinyin):
	slug = ''

	syllables = pinyin.split(' ')
	for i in range(len(syllables)):

		syllable = syllables[i]

		# Check if is valid pinyin
		if len(syllable) < 2 or not syllable[-1].isdigit():
			if syllable == u',' or syllable == u'·':
				slug += '-'
			else:
				# Add dash prefix
				if i > 0 and slug[-1] != u'-':
					slug += u'-'
				# Add non-pinyin character
				slug += syllable

				# Add dash postfix
				if i < len(syllables) - 1:
					slug += '-'
		else:
			slug += syllable
	return slug

# Corrects tones for words with '一' and '不'
def correct_tones(word, pinyin):
	
	# Split pinyin into syllables
	syllables = pinyin.split(' ')

	pinyin = ''
	for i in range(len(word)):
		# Get current character
		character = word[i]

		# Get corresponding pinyin syllable
		syllable = syllables[i]

		# Check if '一' or '不'
		if character == u'\u4e00' or character == u'\u4e0d':
			# If not the last character
			if i + 1 < len(syllables):
				# Extract tone number
				tone = int(syllable[-1])

				# Get tone of next syllable
				next_tone = 0
				if is_cjk(word[i + 1]):
					next_tone = int(syllables[i + 1][-1])

				# Correct tone
				if next_tone == 4:
					tone = 2
				elif next_tone != 5:
					tone = 4
				syllable = syllable[:-1] + str(tone)
		
		# Add syllable to new pinyin string
		pinyin += syllable
		if i + 1 < len(syllables):
			pinyin += ' '

	return pinyin

# Creates a script for Baidu TTS service to pronounce
def create_script(word, pinyin):
	script = ''
	syllables = pinyin.split(' ')
	for i in range(len(word)):
		if syllables[i] == u'，' or syllables[i] == u'·':
			script += u'，'
		else:
			if is_cjk(word[i]):
				script += word[i] + '(' + syllables[i] + ')'
			else:
				script += word[i]
	return script

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
		pinyin = standardize_pinyin(pinyin)

		# Ensure one pinyin syllable for each character
		syllables = pinyin.split(' ')
		if len(syllables) != len(word):
			continue

		# Correct tones
		pinyin = correct_tones(word, pinyin)

		# Append word and pinyin to the list
		words.append(tuple((word, pinyin)))

# Init Baidu speech client
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

for word, pinyin in words:
	# Split pinyin into syllables
	syllables = pinyin.split(' ')

	# Ensure one pinyin syllable for each character
	if len(syllables) != len(word):
		continue

	# Create output filename
	slug = slugify_pinyin(pinyin)
	filename = output_directory + '/' + slug + extension

	# Skip if file already exsis
	if os.path.isfile(filename):
		continue
	
	# Create speech script
	script = create_script(word, pinyin)

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


