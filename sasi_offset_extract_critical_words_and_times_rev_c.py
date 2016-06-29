# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

"""

from process_sasi_list import parse_list
from mnefun import extract_expyfun_events
import mne
import numpy as np

#list_fname = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sentnew2a.lst'
list_fname = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sentnew2a_FishNew.lst'

list_info = parse_list(list_fname)
list_info_temp = list_info



raw_fname = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sasi_101/sasi_101_raw_tsss_mc.fif'
sentnew2_events, _ = extract_expyfun_events(raw_fname)[:2] # Takes 20 seconds
# Format ids
sentnew2_events[:, 2] += 10
sentnew2_events_offset = np.zeros([1500,3], dtype=int)
sentnew2_critical = np.zeros([1500,3], dtype=int)

fname_out = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sasi_101/sentnew2a_FishNew-eve.lst'
#op.join(out_dir, 'ALL_' + (raw_fname) + '-eve.lst')
mne.write_events(fname_out, sentnew2_events)


# NEXT : loop through list_info for each sentence & add offset to timestamp

num_sentences = (len(sentnew2_events)) - 1
# Loop through sentences

total_word_count = 0
last_word = 0
#for sentence_count in range(0, 3):
for sentence_count in range(0, 170): 
    last_word = 0
    for word_count in range(0, len(list_info_temp[1][sentence_count])):
        if word_count == 0:
           # Extract the sentence onset and the event code
           sentence_onset = sentnew2_events[sentence_count,0] # + int(list_info_temp[1][sentence_count][word_count][1])
           sentnew2_events_offset[total_word_count][0]= sentence_onset
           sentnew2_events_offset[total_word_count][2]=sentnew2_events[sentence_count][2] # Event ID
           last_word = last_word + 1
           total_word_count = total_word_count + 1
        else: 
            # Extract all words and times
            word_offset = int(list_info_temp[1][sentence_count][word_count][1] * 1000)
            sentnew2_events_offset[total_word_count][0]= word_offset #0+ sentence_onset
            sentnew2_events_offset[total_word_count][2]= last_word # Which is 1st word?
            last_word = last_word + 1
            total_word_count = total_word_count + 1
#fname_out_sentnew2a = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sasi_107/sentnew2a-eve.lst'
fname_out_sentnew2 = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sasi_101/sentnew2a_FishNew-eve.lst'
mne.write_events(fname_out_sentnew2, sentnew2_events_offset)   

stim_count = 0
# Extract critical words timing
    # If event = 12,13,14,15 then timing aligns with critical word 
    # rev c then no offset
for word_count in range(0, len(sentnew2_events_offset)):
    if sentnew2_events_offset[word_count][2] == 12:
        sentnew2_critical[stim_count][2] = 12
        sentnew2_critical[stim_count][0] = sentnew2_events_offset[word_count + 5][0] + sentnew2_events_offset[word_count][0]
        stim_count = stim_count + 1
    if sentnew2_events_offset[word_count][2] == 13:
        sentnew2_critical[stim_count][2] = 13
        sentnew2_critical[stim_count][0] = sentnew2_events_offset[word_count + 3][0] + sentnew2_events_offset[word_count][0]
        stim_count = stim_count + 1
    if sentnew2_events_offset[word_count][2] == 14:
        sentnew2_critical[stim_count][2] = 14
        sentnew2_critical[stim_count][0] = sentnew2_events_offset[word_count + 6][0] + sentnew2_events_offset[word_count][0]
        stim_count = stim_count + 1
    if sentnew2_events_offset[word_count][2] == 15:
        sentnew2_critical[stim_count][2] = 15
        sentnew2_critical[stim_count][0] = sentnew2_events_offset[word_count + 6][0] + sentnew2_events_offset[word_count][0]
        stim_count = stim_count + 1
    if sentnew2_events_offset[word_count][2] == 16:
        sentnew2_critical[stim_count][2] = 16
        sentnew2_critical[stim_count][0] = sentnew2_events_offset[word_count + 1][0] + sentnew2_events_offset[word_count][0]
        stim_count = stim_count + 1
    

# write new events file
# For mne-python
fname_out_offset = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sasi_101/sasi_101_FishNew_critical-eve_rev_c.lst'
mne.write_events(fname_out_offset, sentnew2_critical)
# For brainstorm
fname_out_offset = '/Volumes/TimeMachineBackups/MEG_Data/SASI/sasi_101/sasi_101_FishNew_critical-eve_rev_c.fif'
mne.write_events(fname_out_offset, sentnew2_critical)

