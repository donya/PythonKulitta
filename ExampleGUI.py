from Tkinter import Tk, Frame, Button, Label, Entry, Text, INSERT, IntVar, Radiobutton, RIGHT,W
from Tkinter import BooleanVar, BOTH, Menu, Menubutton, RAISED, DISABLED, ACTIVE, OptionMenu, StringVar
from Examples import genMusic
import tkMessageBox as mbox
import sys
import midi


class MusicGUI(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        self.centerWindow()
        self.initUI()

    def centerWindow(self):
        w = 500
        h = 500

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def initUI(self):
      
        self.parent.title("Python-Kullita")

        self.pack(fill=BOTH, expand=True)
        # self.var = BooleanVar()
        L1 = Label(self, text="Midi File Name:")
        L1.place(x = 30, y = 450)
        self.fileEntry = Entry(self)
        self.fileEntry.place(x = 150, y = 450)
        genButton = Button(self, text="Genrate Music!",
             command=self.onClick)
        genButton.place(x=350, y=450)
        self.initLog()
        self.init3Voices()

    def init3Voices(self):
        # [(47, 67), (52, 76), (60, 81)])
        # (B,2) - 20
        # (E,3) - 24
        # (C,4) - 25
        self.note_name = ['C','Cs','D','Ds','E','F','Fs','G','Gs','A','As','B']
        self.pitchC1 = StringVar()
        self.pitchC2 = StringVar()
        self.pitchC3 = StringVar()
        self.octave1 = IntVar()
        self.octave2 = IntVar()
        self.octave3 = IntVar()
        self.range1 = IntVar()
        self.range2 = IntVar()
        self.range3 = IntVar()


        v1Label =Label(self, text="Voice 1 start:")
        v1Label.place(x = 30, y = 25)
        self.w1 = OptionMenu(self, self.pitchC1, *self.note_name)
        self.w1.place(x = 135, y = 25)
        self.pitchC1.set(self.note_name[11])
        self.oc1 = OptionMenu(self, self.octave1, *range(1, 9))
        self.oc1.place(x=200, y=25)
        self.octave1.set(2)
        v1_rangeLabel = Label(self, text="Range:")
        v1_rangeLabel.place(x=300, y=25)
        self.rangeoption1 = OptionMenu(self, self.range1, *range(18, 26))
        self.rangeoption1.place(x=360, y=25)
        self.range1.set(20)


        v2Label = Label(self, text="Voice 2 start:")
        v2Label.place(x=30, y=50)
        self.w2 = OptionMenu(self, self.pitchC2, *self.note_name)
        self.w2.place(x=135, y=50)
        self.pitchC2.set(self.note_name[4])
        self.oc2 = OptionMenu(self, self.octave2, *range(1, 9))
        self.oc2.place(x=200, y=25 * 2)
        self.octave2.set(3)
        v2_rangeLabel = Label(self, text="Range:")
        v2_rangeLabel.place(x=300, y=25 * 2)
        self.rangeoption2 = OptionMenu(self, self.range2, *range(18, 26))
        self.rangeoption2.place(x=360, y=25 * 2)
        self.range2.set(24)


        v3Label = Label(self, text="Voice 3 start:")
        v3Label.place(x=30, y=75)
        self.w3 = OptionMenu(self, self.pitchC3, *self.note_name)
        self.w3.place(x=135, y=75)
        self.pitchC3.set(self.note_name[0])
        self.oc3 = OptionMenu(self, self.octave3, *range(1, 9))
        self.oc3.place(x=200, y=25 * 3)
        self.octave3.set(4)
        v3_rangeLabel = Label(self, text="Range:")
        v3_rangeLabel.place(x=300, y=25 * 3)
        self.rangeoption3 = OptionMenu(self, self.range3, *range(18, 26))
        self.rangeoption3.place(x=360, y=25 * 3)
        self.range3.set(25)

    # def pitchClick(self, voiceStr, key):
    #     print("hello!")
    #     vMap = {'1': self.pitchC1, '2': self.pitchC2, '3': self.pitchC3}
    #     txt = voiceStr + ": " + self.note_name[vMap[key].get()]
    #     txt += "\n"
    #     self.logText.insert(INSERT, txt)
    def initLog(self):
        self.logText = Text(self, width = 61, height =21)
        self.logText.insert(INSERT, "Hello.....")
        self.logText.insert(INSERT, "Midi Log:\n")
        self.logText.place(x = 30, y = 110)
        self.logText.config(highlightbackground='blue')

    def onClick(self):
        self.filename = self.fileEntry.get()
        if self.filename == "":
            mbox.showerror("Error", "No File Name!")
            return
        temp = sys.stdout
        sys.stdout = open('log.txt', 'w')
        startPitch = [eval("midi." + self.pitchC1.get() + "_" + str(self.octave1.get())),
                      eval("midi." + self.pitchC2.get() + "_" + str(self.octave2.get())),
                      eval("midi." + self.pitchC3.get() + "_" + str(self.octave3.get())),
                      ]
        print("Start Pitch Value:")
        print(startPitch)
        voiceRange = [(startPitch[0], startPitch[0] + self.range1.get()),
                      (startPitch[1], startPitch[1] + self.range2.get()),
                      (startPitch[2], startPitch[2] + self.range3.get()),
                      ]
        print("3 Voices Pitch Range:")
        print(voiceRange)
        genMusic(self.filename, voiceRange)
        sys.stdout.close()
        sys.stdout = temp
        with open("log.txt", "r") as myfile:
            data = myfile.readlines()
        content = ""
        for line in data:
            content += line
        self.logText.insert(INSERT, content)
        mbox.showinfo("Music Generation", self.filename + ".midi File completed")


def main():
  
    root = Tk()
    # root.geometry("250x150+300+300")
    app = MusicGUI(root)
    root.mainloop()
    # print eval('midi.G_3')


if __name__ == '__main__':
    main()  