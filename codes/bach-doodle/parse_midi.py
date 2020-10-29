import json
import magenta
import note_seq
from note_seq.protobuf import music_pb2 as mpb
import os
import os.path as osp

input_dir = '/u/ys4aj/YuchenSun/Course/CS4710/AI_PROJECT/codes/bach-doodle/infile/'
infile = osp.join(input_dir,'2020-10-28_224250_1.midi')

seq = note_seq.midi_file_to_note_sequence(infile)
ori = [i for i in seq.notes if i.end_time <= 8.0]
comb = [i for i in seq.notes if i.start_time >= 8.0]
comb2 = [i for i in seq.notes if i.start_time >= 8.0]

def equal(note1,note2):
    if note1.start_time:
        note1.start_time = 0.0
    dur1, dur2 = note1.end_time-note1.start_time, note2.end_time-note2.start_time
    return dur1 == dur2 and note1.pitch == note2.pitch

new = set()

for o in ori:
    for c in comb2:
        if equal(o,c):
            comb2.remove(c)


print(comb2)