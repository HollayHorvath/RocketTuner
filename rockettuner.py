# RocketTuner - a tuner that rocks!
# Copyright (C) 2016, Zsombor Hollay-Horvath (hollay.horvath@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gdk, Gst

from collections import namedtuple

Note = namedtuple('Note', ['octave', 'note'])

Range = namedtuple('Range', ['start', 'end'])

class RocketTuner:

    octaveRanges = Range(start = 0, end = 9)

    defaultFreq = 440.0

    octaves = tuple(range(octaveRanges.start, octaveRanges.end))
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
        'F#', 'G', 'G#', 'A', 'A#', 'B', 'C+']

    scales = {
        'Equal Temperament':
            tuple((2 ** (1/12)) ** x
                for x in range(12)),
        'Werckmeister I (III)': (
            1.0000000000000000, # C,  1/1
            1.0534979423868314, # C#, 256/243
            1.1174033085417048, # D,  64/81 * 2**(1/2)
            1.1851851851851851, # D#, 32/27
            1.2528272487271466, # E,  256/243 * 2**(1/4)
            1.3333333333333333, # F,  4/3
            1.4046639231824416, # F#, 1024/729
            1.4949269604510480, # G,  8/9 * 8**(1/4)
            1.5802469135802468, # G#, 128/81
            1.6704363316361952, # A,  1024/729 * 2**(1/4)
            1.7777777777777777, # A#, 16/9
            1.8792408730907195  # B,  128/81 * 2**(1/4)
        ),
        'Werckmeister II (IV)': (
            1.0000000000000000, # C,  1/1
            1.0487500117602806, # C#, 16384/19683 * 2**(1/3)
            1.1199298221287761, # D,  8/9 * 2**(1/3)
            1.1851851851851851, # D#, 32/27
            1.2542428064933920, # E,  64/81 * 4**(1/3)
            1.3333333333333333, # F,  4/3
            1.4046639231824416, # F#, 1024/729
            1.4932397628383682, # G,  32/27 * 2**(1/3)
            1.5731250176404208, # G#, 8192/6561 * 2**(1/3)
            1.6723237419911896, # A,  256/243 * 4**(1/3)
            1.7858261834642244, # A#, 9/(4 * 2**(1/3))
            1.8728852309099222  # B,  4096/2187
        ),
        'Werckmeister III (V)': (
            1.0000000000000000, # C,  1/1
            1.0570729911135297, # C#, 8/9*2**(1/4)
            1.1250000000000000, # D,  9/8
            1.1892071150027210, # D#, 2**(1/4)
            1.2570787221094177, # E,  8/9*2**(1/2)
            1.3378580043780612, # F,  9/8*2**(1/4)
            1.4142135623730951, # F#  2**(1/2)
            1.5000000000000000, # G,  3/2
            1.5802469135802468, # G#, 128/81
            1.6817928305074290, # A,  8**(1/4)
            1.7838106725040817, # A#, 3/(8**(1/4))
            1.8856180831641267  # B,  4/3*2**(1/2)
        ),
        'Werckmeister IV (VI)': (
            1.0000000000000000, # C,  1/1
            1.0537634408602150, # C#, 98/93
            1.1136363636363635, # D,  49/44
            1.1878787878787880, # D#, 196/165
            1.2564102564102564, # E,  49/39
            1.3333333333333333, # F,  4/3
            1.4100719424460430, # F#, 196/139
            1.4961832061068703, # G,  196/131
            1.5806451612903225, # G#, 49/31
            1.6752136752136753, # A,  196/117
            1.7818181818181817, # A#, 98/55
            1.8846153846153846  # B,  49/26
        )
    }

    @classmethod
    def noteDiff(cls, tuning, audible):
        return Note(octave = audible[0] - tuning[0],
            note = cls.notes.index(audible[1]) - cls.notes.index(tuning[1]))

    def __init__(self):
        ''' Gst/Glade/Gtk init'''
        Gst.init_check()

        self.audio = Gst.Pipeline(name='note')
        self.audioSource = Gst.ElementFactory.make('audiotestsrc', 'src')
        sink = Gst.ElementFactory.make('autoaudiosink', 'output')

        self.audio.add(self.audioSource)
        self.audio.add(sink)
        self.audioSource.link(sink)

        self.gladefile = 'rockettuner.glade'
        self.builder = Gtk.Builder()

        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)

        self.window = self.builder.get_object('rockettuner')
        self.window.set_icon_from_file('icon/icon64.png')

        ''' Get objects '''
        self.tuningFreqObj = self.builder.get_object('entry_tuningFreq')

        self.tuningNoteObj = self.builder.get_object('combo_tuningNote')
        self.tuningOctaveObj = self.builder.get_object('combo_tuningOctave')

        self.audibleFreqObj = self.builder.get_object('label_audibleFreq')

        self.audibleNoteObj = self.builder.get_object('combo_audibleNote')
        self.audibleOctaveObj = self.builder.get_object('combo_audibleOctave')

        self.tuningScaleObj = self.builder.get_object('combo_tuningScale')

        ''' Actual init '''
        self.tuningFreq = self.defaultFreq
        self.audibleFreq = self.audibleFreq

    ''' Attributes '''
    @property
    def tuningFreq(self):
        try:
            return float(self.tuningFreqObj.get_text())
        except ValueError:
            return 'N/A'

    @tuningFreq.setter
    def tuningFreq(self, value):
        self.tuningFreqObj.set_text(str(value))

    @property
    def audibleFreq(self):
        tuningFreq = self.tuningFreq

        if type(tuningFreq) != float:
            return 'N/A'

        tuning = (self.tuningOctave, self.tuningNote)
        audible = (self.audibleOctave, self.tuningNote)

        octaves, notes = self.noteDiff(tuning, audible)

        return tuningFreq * (2**octaves) * self.scales[self.tuningScale][notes]

    @audibleFreq.setter
    def audibleFreq(self, value):
        if type(value) == float:
            audibleFreq = '%.2f'%value
            self.audioSource.set_property('freq', value)
        else:
            audibleFreq = 'N/A'

        self.audibleFreqObj.set_text('Audible frequency: %s Hz'%audibleFreq)

    @property
    def tuningNote(self):
        return self.notes[self.tuningNoteObj.get_active()]

    @tuningNote.setter
    def tuningNote(self, value):
        self.tuningNoteObj.set_active(self.notes.index(value))

    @property
    def tuningOctave(self):
        return self.tuningOctaveObj.get_active()

    @tuningOctave.setter
    def tuningOctave(self, value):
        self.tuningOctaveObj.set_active(value)

    @property
    def audibleNote(self):
        return self.notes[self.audibleNoteObj.get_active()]

    @audibleNote.setter
    def audibleNote(self, value):
        self.audibleNoteObj.set_active(self.notes.index(value))

    @property
    def audibleOctave(self):
        return self.audibleOctaveObj.get_active()

    @audibleOctave.setter
    def audibleOctave(self, value):
        self.audibleOctaveObj.set_active(value)

    @property
    def tuningScale(self):
        return self.tuningScaleObj.get_active_text()


    ''' Event handlers '''
    def onTuningFreqChanged(self, obj):
        pass

    def onTuningFreqClicked(self, obj):
        pass

    def onTuningOctaveChanged(self, obj):
        pass

    def onTuningOctaveClicked(self, obj):
        pass

    def onTuningOctaveScrolled(self, obj):
        pass

    def onTuningNoteChanged(self, obj):
        pass

    def onTuningNoteClicked(self, obj):
        pass

    def onTuningNoteScrolled(self, obj):
        pass

    def onAudibleNoteChanged(self, obj):
        pass

    def onAudibleNoteClicked(self, obj):
        pass

    def onAudibleNoteScrolled(self, obj):
        pass

    def onAudibleOctaveChanged(self, obj):
        pass

    def onAudibleOctaveClicked(self, obj):
        pass

    def onAudibleOctaveScrolled(self, obj):
        pass

    def onTuningScaleChanged(self, obj):
        pass

    def onTuningScaleScrolled(self, obj):
        pass

    def onPlayClicked(self, obj):
        if obj.get_active():
            self.audio.set_state(Gst.State.PLAYING)
        else:
            self.audio.set_state(Gst.State.NULL)

    def onDeleteWindow(self, obj, data):
        Gtk.main_quit()

    def show_all(self):
        self.window.show()

if __name__ == '__main__':

    window = RocketTuner()
    window.show_all()

    Gtk.main()
