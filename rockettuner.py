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

class GrafiteWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='RocketTuner')
        self.set_icon_from_file('icon/icon64.png')

        ''' Main values '''
        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.octaves = list(range(9))

        self.tuningFreq = 440
        self.tuningNote = 'A'
        self.tuningOctave = 4

        self.audibleFreq = 440
        self.audibleNote = 'A'
        self.audibleOctave = 4

        self.root = 2 ** (1 / 12)

        self.volume = 1.0

        self.buttonTrigger = False
        self.buttonTimeout = None

        ''' Set window values '''
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)

        self.connect('delete-event', Gtk.main_quit)

        grid = Gtk.Grid(column_spacing=10, row_spacing=6)
        self.add(grid)

        ''' Tuning freq '''
        labelTuningFreq = Gtk.Label('Tuning frequency')

        self.entryTuningFreq = Gtk.Entry()
        self.entryTuningFreq.set_text('%0.2f'%self.tuningFreq)

        labelEntryTuningFreq = Gtk.Label('Hz')

        buttonTuningFreqUp = Gtk.Button()
        buttonTuningFreqUp.set_label('+')

        buttonTuningFreqDown = Gtk.Button()
        buttonTuningFreqDown.set_label('-')

        # Callbacks
        self.entryTuningFreq.connect('changed', self.changedTuningFreq)
        buttonTuningFreqUp.connect('clicked', self.changedTuningFreq)
        buttonTuningFreqDown.connect('clicked', self.changedTuningFreq)

        # Grid
        grid.attach(labelTuningFreq, 0, 0, 6, 1)
        grid.attach(self.entryTuningFreq, 0, 1, 3, 1)
        grid.attach(labelEntryTuningFreq, 3, 1, 1, 1)

        grid.attach(buttonTuningFreqUp, 4, 1, 1, 1)
        grid.attach(buttonTuningFreqDown, 5, 1, 1, 1)

        ''' Tuning note/octave '''
        labelTuningNote = Gtk.Label('Tuning note')

        storeTuningNote = Gtk.ListStore(str)
        for note in self.notes:
            storeTuningNote.append([note])

        rendererTuningNote = Gtk.CellRendererText()

        self.comboTuningNote = Gtk.ComboBox.new_with_model(storeTuningNote)
        self.comboTuningNote.pack_start(rendererTuningNote, True)
        self.comboTuningNote.add_attribute(rendererTuningNote, 'text', 0)
        self.comboTuningNote.set_active(9)

        buttonTuningNoteUp = Gtk.Button()
        buttonTuningNoteUp.set_label('+')

        buttonTuningNoteDown = Gtk.Button()
        buttonTuningNoteDown.set_label('-')

        labelTuningOctave = Gtk.Label('Tuning octave')

        storeTuningOctave = Gtk.ListStore(int)
        for octave in self.octaves:
            storeTuningOctave.append([octave])

        rendererTuningOctave = Gtk.CellRendererText()

        self.comboTuningOctave = Gtk.ComboBox.new_with_model(storeTuningOctave)
        self.comboTuningOctave.pack_start(rendererTuningOctave, True)
        self.comboTuningOctave.add_attribute(rendererTuningOctave, 'text', 0)
        self.comboTuningOctave.set_active(4)

        buttonTuningOctaveUp = Gtk.Button()
        buttonTuningOctaveUp.set_label('+')

        buttonTuningOctaveDown = Gtk.Button()
        buttonTuningOctaveDown.set_label('-')

        # Callbacks
        self.comboTuningNote.connect('scroll-event', self.scrolledTuningNote)
        self.comboTuningNote.connect('changed', self.changedTuningNote)
        buttonTuningNoteUp.connect('clicked', self.changedTuningNote)
        buttonTuningNoteDown.connect('clicked', self.changedTuningNote)

        self.comboTuningOctave.connect('changed', self.changedTuningOctave)
        buttonTuningOctaveUp.connect('clicked', self.changedTuningOctave)
        buttonTuningOctaveDown.connect('clicked', self.changedTuningOctave)

        # Grid
        grid.attach(labelTuningNote, 0, 3, 3, 1)
        grid.attach(self.comboTuningNote, 0, 4, 1, 1)

        grid.attach(buttonTuningNoteUp, 1, 4, 1, 1)
        grid.attach(buttonTuningNoteDown, 2, 4, 1, 1)

        grid.attach(labelTuningOctave, 3, 3, 3, 1)
        grid.attach(self.comboTuningOctave, 3, 4, 1, 1)

        grid.attach(buttonTuningOctaveUp, 4, 4, 1, 1)
        grid.attach(buttonTuningOctaveDown, 5, 4, 1, 1)

        ''' Audible note/octave '''
        labelAudibleNote = Gtk.Label('Audible note')

        storeAudibleNote = Gtk.ListStore(str)
        for note in self.notes:
            storeAudibleNote.append([note])

        rendererAudibleNote = Gtk.CellRendererText()
        self.comboAudibleNote = Gtk.ComboBox.new_with_model(storeAudibleNote)
        self.comboAudibleNote.pack_start(rendererAudibleNote, True)
        self.comboAudibleNote.add_attribute(rendererAudibleNote, 'text', 0)
        self.comboAudibleNote.set_active(9)

        buttonAudibleNoteUp = Gtk.Button()
        buttonAudibleNoteUp.set_label('+')

        buttonAudibleNoteDown = Gtk.Button()
        buttonAudibleNoteDown.set_label('-')

        labelAudibleOctave = Gtk.Label('Audible octave')

        storeAudibleOctave = Gtk.ListStore(int)
        for octave in self.octaves:
            storeAudibleOctave.append([octave])

        rendererAudibleOctave = Gtk.CellRendererText()
        self.comboAudibleOctave = Gtk.ComboBox.new_with_model(storeAudibleOctave)
        self.comboAudibleOctave.pack_start(rendererAudibleOctave, True)
        self.comboAudibleOctave.add_attribute(rendererAudibleOctave, 'text', 0)
        self.comboAudibleOctave.set_active(4)

        buttonAudibleOctaveUp = Gtk.Button()
        buttonAudibleOctaveUp.set_label('+')

        buttonAudibleOctaveDown = Gtk.Button()
        buttonAudibleOctaveDown.set_label('-')

        # Callbacks
        self.comboAudibleNote.connect('scroll-event', self.scrolledAudibleNote)
        self.comboAudibleNote.connect('changed', self.changedAudibleNote)
        buttonAudibleNoteUp.connect('clicked', self.changedAudibleNote)
        buttonAudibleNoteDown.connect('clicked', self.changedAudibleNote)

        self.comboAudibleOctave.connect('changed', self.changedAudibleOctave)
        buttonAudibleOctaveUp.connect('clicked', self.changedAudibleOctave)
        buttonAudibleOctaveDown.connect('clicked', self.changedAudibleOctave)

        # Grid
        grid.attach(labelAudibleNote, 0, 5, 3, 1)
        grid.attach(self.comboAudibleNote, 0, 6, 1, 1)

        grid.attach(buttonAudibleNoteUp, 1, 6, 1, 1)
        grid.attach(buttonAudibleNoteDown, 2, 6, 1, 1)

        grid.attach(labelAudibleOctave, 3, 5, 3, 1)
        grid.attach(self.comboAudibleOctave, 3, 6, 1, 1)

        grid.attach(buttonAudibleOctaveUp, 4, 6, 1, 1)
        grid.attach(buttonAudibleOctaveDown, 5, 6, 1, 1)

        ''' Audible freq, misc '''
        self.labelAudibleFreq = Gtk.Label('Audible frequency: %0.2f Hz'%self.audibleFreq)

        buttonVolume = Gtk.VolumeButton()
        buttonVolume.set_value(self.volume)

        buttonPlay = Gtk.ToggleButton('▶')

        # Callbacks
        buttonVolume.connect('value-changed', self.changeVolume)
        buttonPlay.connect('clicked', self.clickPlay)

        # Grid
        grid.attach(self.labelAudibleFreq, 0, 7, 3, 1)

        grid.attach(buttonVolume, 3, 7, 2, 1)
        grid.attach(buttonPlay, 5, 7, 1, 1)

        ''' Audio settings '''
        self.audio = Gst.Pipeline(name='note')
        self.source = Gst.ElementFactory.make('audiotestsrc', 'src')
        sink = Gst.ElementFactory.make('autoaudiosink', 'output')

        self.audio.add(self.source)
        self.audio.add(sink)
        self.source.link(sink)

    def noteDiff(self):
        return (self.audibleOctave-self.tuningOctave) * 12 + self.notes.index(self.audibleNote) - self.notes.index(self.tuningNote)

    def calcAudibleFreq(self):
        self.audibleFreq = self.tuningFreq*(self.root**self.noteDiff())

    def play(self):
        self.audio.set_state(Gst.State.PLAYING)

    def stop(self):
        self.audio.set_state(Gst.State.NULL)

    def changeVolume(self, obj, volume):
        self.volume = volume
        #TODO: how to change volume?
        #~self.audio.set_state(Gst.State.NULL)
        #~self.audio.volume = self.volume
        #~self.audio.set_state(Gst.State.PLAYING)
        pass

    def clickPlay(self, obj):
        if obj.get_active():
            self.play()
        else:
            self.stop()

    def changeFreq(self):
        self.calcAudibleFreq()
        self.labelAudibleFreq.set_label('Audible frequency: %0.2f Hz'%self.audibleFreq)
        self.source.set_property('freq', self.audibleFreq)

    def changedTuningFreq(self, obj):
        try:
            tuningFreq = float(self.entryTuningFreq.get_text())
            if type(obj) == Gtk.Button:
                label = obj.get_label()
                if label == '+':
                    tuningFreq += 1
                elif label == '-':
                    tuningFreq -= 1
                self.entryTuningFreq.set_text(str(tuningFreq))
            self.tuningFreq = tuningFreq
            self.changeFreq()
        except:
            pass

    def changedTuningNote(self, obj):
        #!!! TODO add plus-minus
        self.tuningNote = self.notes[self.comboTuningNote.get_active()]
        self.tuningOctave = self.comboTuningOctave.get_active()

        self.changeFreq()

    def changedTuningOctave(self, obj):
        #!!! TODO add plus-minus
        self.tuningOctave = self.comboTuningOctave.get_active()

        self.changeFreq()

    def scrolledTuningNote(self, obj, val):
        if val.direction == Gdk.ScrollDirection.UP:
            self.changeTuning(-1)
        elif val.direction == Gdk.ScrollDirection.DOWN:
            self.changeTuning(1)

    def changeTuning(self, direction):
        note = self.comboTuningNote.get_active()
        octave = self.comboTuningOctave.get_active()

        diff = note + direction
        if diff < 0 and octave > 0:
            note = 11
            octave -= 1
        elif diff > 11 and octave < 8:
            note = 0
            octave += 1

        self.comboTuningNote.set_active(note)
        self.comboTuningOctave.set_active(octave)

    def changedAudibleNote(self, obj):
        #!!! TODO add plus-minus
        self.audibleNote = self.notes[self.comboAudibleNote.get_active()]
        self.audibleOctave = self.comboAudibleOctave.get_active()

        self.changeFreq()

    def changedAudibleOctave(self, obj):
        #!!! TODO add plus-minus
        self.audibleOctave = self.comboAudibleOctave.get_active()

        self.changeFreq()

    def scrolledAudibleNote(self, obj, val):
        if val.direction == Gdk.ScrollDirection.UP:
            self.changeAudible(-1)
        elif val.direction == Gdk.ScrollDirection.DOWN:
            self.changeAudible(1)

    def changeAudible(self, direction):
        note = self.comboAudibleNote.get_active()
        octave = self.comboAudibleOctave.get_active()

        diff = note + direction
        if diff < 0 and octave > 0:
            note = 11
            octave -= 1
        elif diff > 11 and octave < 8:
            note = 0
            octave += 1

        self.comboAudibleNote.set_active(note)
        self.comboAudibleOctave.set_active(octave)

if __name__ == '__main__':

    Gst.init_check()

    window = GrafiteWindow()
    window.show_all()

    Gtk.main()
