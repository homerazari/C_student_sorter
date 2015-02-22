#!/usr/bin/python
from PIL import Image
from subprocess import Popen, PIPE, check_output
import os
from sys import argv

def thug_func(input_thug):

	input_thug = argv
	print input_thug
	count = 'ffprobe -show_streams -count_frames -i ' + input_thug[1]
	eq = '='

	output_1 = Popen(count, shell=True, stdout=PIPE)
	output_1.wait()

	frame_grep = check_output(('grep', 'nb_frames='), stdin=output_1.stdout)  
	split = frame_grep.splitlines()[0]
	x = split.find(eq)
	num = split[x+1:]
	num = int(num)-1
	last_frame = [
		'ffmpeg', '-y',
		'-i', input_thug[1],
		'-vf', "select='eq(n\,{})'".format(num),
		'-vframes', '1', 'last_f.png'
		]

	output_2 = Popen(last_frame, stdout=PIPE)
	output_2.wait()

	lf_load = Image.open('last_f.png', 'r')
	alpha_load = Image.open('alpha.png', 'r')
	bg_load = Image.open('bg.png', 'r')
	alpha_load = alpha_load.resize(lf_load.size, Image.ANTIALIAS)
	bg_load = bg_load.resize(lf_load.size, Image.ANTIALIAS)	
	comp_pre = Image.composite(lf_load, alpha_load, alpha_load)
	comp_pre = Image.alpha_composite(comp_pre, bg_load)
	comp_pre.save('composed.png', 'PNG')

	comp = [
		'ffmpeg', '-loop', '1', '-y', 
		'-i', 'composed.png',
		'-i', 'rap.mp4', 
		'-c:v', 'mpeg2video', '-q:v', '5', '-q:a', '1',  
		'-r', '30', '-t', '5',
		'-vf', "zoompan=z='min(zoom+0.0015,1.5)':\
		d=300:x='if(gte(zoom,1.5),x,x+201/a)':\
		y='if(gte(zoom,1.5),y,y+1)'",
		'comp.mpg'
		]

	output_3 = Popen(comp, stdout=PIPE)
	output_3.wait()

	inter_src = [
		'ffmpeg', '-y',
		'-i', input_thug[1],
		'-c:v', 'mpeg2video', '-q:v', '10',
		'-q:a', '1', '-s', '1280x720', 
		'inter.mpg'
		]

	output_4 = Popen(inter_src,  stdout=PIPE)
	output_4.wait()

	concat_1 = [ 	
		'ffmpeg -i "concat:inter.mpg|comp.mpg"\
		 -y -r 30 -c:v libvpx -b:v 1M -q:v 1 thuglife.webm'
		]

	output_5 = Popen(concat_1, shell=True, stdout=PIPE)	
	output_5.wait()


if __name__ == '__main__':
	thug_func(argv[1])
