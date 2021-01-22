import os
import subprocess
from sys import argv
import re
import math

# A little script to encode video as .mkv using the Intel (Quicksync) hardware encoding. 
# You'll need to check the support for your machine. Basic ffmpeg scripts pulled from
# <https://youtu.be/J6mwh-Jikp8>, along with links to check processor support.

# Desired Resolution
resolution = "scale='1920:1080'" # for 1080p, '720:576' for DVD

# how long to run with 'default' ffmpeg software encoding to get a representative bitrate.
processing_time = 10

# how much to round up the identified bitrate to get a good value for the hardware encoding.
round_up = 300

full_filename = argv[1]
filename = os.path.splitext(full_filename)[0]

# tidy temp file from working directory, change as per cwd
os.chdir('/Volumes/Scratch/Pi-Media/')
if os.path.isfile('test_default.mkv'):
  os.remove('test_default.mkv')

# run pre-processing to get a reasonable bitrate, and catch the output
print('\nPraying to the bitrate gods for ' + str(processing_time) + ' secs, they say...\n')
task = (['ffmpeg', '-i', full_filename, '-acodec', 'copy', '-vcodec', 'libx264', 'test_default.mkv'])
try:
  output = subprocess.run(task, timeout = processing_time, text = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
  print("The video is probably too short to be useful, perhaps delete it?\n")
  exit()
except subprocess.TimeoutExpired as error_instance:
  if os.path.isfile('test_default.mkv'):
    os.remove('test_default.mkv')
    
# extract the bitrate and lift it a bit
  output_bitrate = re.findall(r'bitrate=\W*(\d+)', error_instance.stdout.decode())
  bitrate = math.ceil((int(output_bitrate[-1]))/round_up)* round_up

print('the bitrate is ' + str(bitrate) + '.\nStarting the re-encode...\n')

# remove existing .mkv, if there
if os.path.isfile(filename + '.mkv'):
  os.remove(filename + '.mkv')

# encode the file
task = (["ffmpeg", "-hide_banner", "-i", str(full_filename), "-vf", resolution, "-acodec", "copy", "-vcodec", "hevc_videotoolbox", "-b:v", str(bitrate) + "k", str(filename) + ".mkv"])
try:
  subprocess.run(task)
except:
  print('Some error')
print('Done.\n')