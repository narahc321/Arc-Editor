import tkinter as tk
from .ColorLight_LineNumbers import ColorLight, LineMain
import tkinter as Tkinter
import sys
import os


class TextPad(Tkinter.Text):
	def __init__(self, *args, **kwargs):
		Tkinter.Text.__init__(self, *args, **kwargs)
		self.storeobj = {"Root": self.master}
		LineMain(self)
		ColorLight(self)
		self.pack(expand = True, fill = "both")


if __name__ == '__main__':
	root = Tkinter.Tk(className = " Test TextPad")
	# root.call('wm', 'iconphoto', self._w, tk.PhotoImage(file='img.png'))
	TextPad(root)
	root.mainloop()


class TextPad_Window(tk.Tk):
	# os.system("gcc -Wall xc.c -o compiler")	
	os.system("lex c.l")
	os.system("yacc c.y")
	os.system("cc lex.yy.c y.tab.c -ll -o compiler")
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self._text_pad_()


	def _text_pad_(self):
		self.call('wm', 'iconphoto', self._w, tk.PhotoImage(file='libs/img.png'))
		TextPad(self).pack()
		return

