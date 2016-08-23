# -*- coding: utf-8 -*-
"""
Convert original WAV files to TDT sample rate and re-normalize
"""

import os
import os.path as op

import numpy as np

from expyfun.stimuli import read_wav, write_wav, resample, rms


def parse_list(fname):
    """Parse a .lst stimulus file into filenames, codes, and isis"""
    with open(fname, 'r') as fid:
        lines = fid.readlines()
    names = list()
    codes = list()
    isis = list()
    while(len(lines) > 0):
        line = lines.pop(0)  # take the next line
        if line.startswith('//'):  # comment, skip
            continue
        # this should be a header line for the given stimulus
        line = line.strip().split()  # split it on whitespace
        assert len(line) == 10  # must have 8 parts
        # distribute to easier to understand name
        # XXX "balance" in the comment seems to store the line count!
        name, code, duration, isi, iti, balance, volume, count, x, xx = line
        assert int(x) == 0  # No idea what these last two entries are...
        assert int(xx) == 6
        count = int(count)
        assert count in (6, 7, 8)  # 7 or 8 parts
        assert int(volume) == 0  # ???
        names.append(name)
        isis.append(int(isi) / 1000.)  # to seconds
        assert isis[-1] == 2.  # might not always be true, but seems to be
        codes.append([[int(code), int(duration)]])
        assert codes[-1][0][0] in (10, 20, 30, 40, 50)
        for ci in range(count):
            line = lines.pop(0).strip().split()
            assert len(line) == 2
            codes[-1].append([int(line[0]), int(line[1]) / 1000.])  # ms->sec
        assert len(codes[-1]) == count + 1
    assert len(names) == len(codes) == len(isis)
    return names, codes, isis


if __name__ == '__main__':
    stim_dir = 'Stimuli'
    out_dir = 'stimuli_resampled'
    fs = 44100
    fs_out = 24414
    rms_out = 0.01  # normalize them to have about 0.01 RMS
    dB_out = 65
    if not op.isdir(out_dir):
        os.mkdir(out_dir)
    list_names = ['sentnew2a.lst', 'sentnew2b.lst']  # list names
    # These lists have the same set of stimuli, right?
    names, codes, isis = parse_list(op.join(stim_dir, list_names[0]))
    names_b, codes_b, isis_b = parse_list(op.join(stim_dir, list_names[1]))
    assert set(names) == set(names_b)
    list_name = list_names[0]  # okay, just process one then
    del list_names

    datas = list()
    print('Reading and resampling stimuli...')
    for ii, (name, code) in enumerate(zip(names, codes)):
        data, fs_read = read_wav(op.join(stim_dir, name), verbose=False)
        assert fs == fs_read
        assert (data[0] == data[1]).all()
        data = data[0]  # one channel
        datas.append(resample(data, fs_out, fs, npad='auto'))
        assert np.isclose(datas[-1].shape[-1] / float(fs_out),
                          data.shape[-1] / float(fs), atol=1e-3)  # 1 ms
    assert len(datas) == len(names)
    rmss = [rms(d) for d in datas]
    factor = rms_out / np.mean(rmss)
    print('Writing stimuli...')
    for name, data in zip(names, datas):
        data *= factor  # RMS mean across stimuli is now our desired value
        write_wav(op.join(out_dir, name), data, fs_out, verbose=False,
                  overwrite=True)
    rmss = np.array([rms(d) for d in datas])
    assert np.isclose(np.mean(rmss), rms_out)
    play_rmss = dB_out + 20 * np.log10(rmss / rms_out)
    print('Assuming a %s dB SPL set in ExperimentController, stimuli will '
          'play with a long-term RMS of:\n[%0.1f, %0.1f] dB'
          % (dB_out, play_rmss.min(), play_rmss.max()))
