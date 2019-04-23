import builtins as __builtin__
import re
import keyword
import tkinter
import tkinter as tk
from subprocess import Popen, PIPE
import subprocess
import os

# import sys
# import re
# import shlex


breakpoints = []
def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"


def ty():
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(__builtin__)
                                        if not name.startswith('_')]
    builtinlist.remove('print')
    builtinlist.append('#include')
    builtinlist.append('#define')
    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"//[^\n]*"])
    stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    return kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any("SYNC", [r"\n"])

def _coordinate(start,end,string):
    srow=string[:start].count('\n')+1 # starting row
    scolsplitlines=string[:start].split('\n')
    if len(scolsplitlines)!=0:
        scolsplitlines=scolsplitlines[len(scolsplitlines)-1]
    scol=len(scolsplitlines)# Ending Column
    lrow=string[:end+1].count('\n')+1
    lcolsplitlines=string[:end].split('\n')
    if len(lcolsplitlines)!=0:
        lcolsplitlines=lcolsplitlines[len(lcolsplitlines)-1]
    lcol=len(lcolsplitlines)+1# Ending Column
    return '{}.{}'.format(srow, scol),'{}.{}'.format(lrow, lcol)#, (lrow, lcol)

def coordinate(pattern, string,txt):
    line=string.splitlines()
    start=string.find(pattern)  # Here Pattern Word Start
    end=start+len(pattern) # Here Pattern word End
    srow=string[:start].count('\n')+1 # starting row
    scolsplitlines=string[:start].split('\n')
    if len(scolsplitlines)!=0:
        scolsplitlines=scolsplitlines[len(scolsplitlines)-1]
    scol=len(scolsplitlines)# Ending Column
    lrow=string[:end+1].count('\n')+1
    lcolsplitlines=string[:end].split('\n')
    if len(lcolsplitlines)!=0:
        lcolsplitlines=lcolsplitlines[len(lcolsplitlines)-1]
    lcol=len(lcolsplitlines)# Ending Column
    return '{}.{}'.format(srow, scol),'{}.{}'.format(lrow, lcol)#, (lrow, lcol)

def check(k={}):
    if k['COMMENT']!=None:
        return 'comment','gray'
    elif k['BUILTIN']!=None:
        return 'builtin','VioletRed'
    elif k['STRING']!=None:
        return 'string','green'
    elif k['KEYWORD']!=None:
        return 'keyword','orange'
    else:
        return 'ss','NILL'

txtfilter=re.compile(ty(),re.S)


class ColorLight:
    def __init__(self, txtbox=None):
        self.txt=txtbox
        self.txt.bind("<Any-KeyPress>", self.trigger)

    def binding_functions_configuration(self):
        self.txt.storeobj['ColorLight']=self.trigger
        return

    def trigger(self, event=None):

        global breakpoints
        breakpoints = []
        val=self.txt.get('1.0','end')
        file = open("hello.c","w")
        file.write(val)
        file.close()

        # p = subprocess.Popen("./compiler < hello.c", stdout=subprocess.PIPE, shell=True)
        # (output, err) = p.communicate()
        # p_status = p.wait()
        # # print(output)
        # line = output
        # if not isinstance(line, int):
        #     er = re.findall(r"hello.c:\d+:",line.decode('utf-8'))
        #     if len(er) > 0:
        #         ln_no = int(er[0][8:len(er[0])-1],10)
        #         breakpoints.append(ln_no) 


        p = subprocess.Popen('gcc hello.c -fsyntax-only', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout
        for line in out:
            print(line)
            er = re.findall(r"hello.c:\d+:",line.decode('utf-8'))
            if len(er) > 0:
                ln_no = int(er[0][8:len(er[0])-1],10)
                breakpoints.append(ln_no)
        
        if len(val)==1:
            return
        for i in ['comment','builtin','string','keyword']:
            self.txt.tag_remove(i,'1.0','end')
        for i in txtfilter.finditer(val):
            start=i.start()
            end=i.end()-1
            #print start,end
            tagtype,color=check(k=i.groupdict())
            if color!='NILL':
                ind1,ind2=_coordinate(start,end,val)
                #print ind1, ind2
                self.txt.tag_add(tagtype,ind1, ind2)
                self.txt.tag_config(tagtype,foreground=color)
                #Tkinter.Text.tag_configure
#        for i in idprog.finditer(val):
#            start=i.start()
#            end=i.end()-1
#            ind1,ind2=_coordinate(start,end,val)
#            self.txt.tag_add('BLUE',ind1, ind2)
#            self.txt.tag_config("BLUE",foreground='grey')
#            #Tkinter.Text.tag_configure


class LineNumberCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.text_widget = None
        # self.breakpoints = []

    def connect(self,text_widget):
        self.text_widget = text_widget

    def re_render(self):
        global breakpoints
        """Re-render the line canvas"""
        self.delete('all') # To prevent drawing over the previous canvas

        temp = self.text_widget.index("@0,0")
        while True :
            dline= self.text_widget.dlineinfo(temp)
            if dline is None: 
                break
            y = dline[1]
            x = dline[0]
            linenum = str(temp).split(".")[0]

            id = self.create_text(2,y,anchor="nw", text=linenum)

            if int(linenum) in breakpoints:                
                x1,y1,x2,y2 = self.bbox(id)
                self.create_oval(x1,y1,x2,y2,fill='red')
                self.tag_raise(id)

            temp = self.text_widget.index("%s+1line" % temp)
            
            

class LineMain:
    def __init__(self, text):
        self.text = text
        self.master = text.master
        self.mechanise()
        self._set_()
        self.binding_keys()

    def mechanise(self):
        self.text.tk.eval('''
            proc widget_interceptor {widget command args} {

                set orig_call [uplevel [linsert $args 0 $command]]

              if {
                    ([lindex $args 0] == "insert") ||
                    ([lindex $args 0] == "delete") ||
                    ([lindex $args 0] == "replace") ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Changed>>
                }

                #return original command
                return $orig_call
            }
            ''')
        self.text.tk.eval('''
            rename {widget} new
            interp alias {{}} ::{widget} {{}} widget_interceptor {widget} new
        '''.format(widget=str(self.text)))
        return


    def binding_keys(self):
        for key in ['<Down>','<Up>',"<<Changed>>","<Configure>"]:
            self.text.bind(key, self.changed)
        return

    def changed(self, event):
        self.linenumbers.re_render()
        #print "render"
        return


    def _set_(self):
        self.linenumbers = LineNumberCanvas(self.master, width=30)
        self.linenumbers.connect(self.text)
        self.linenumbers.pack(side="left", fill="y")
        return       



if __name__ == '__main__':
    root=Tkinter.Tk()
    txt=Tkinter.Text(root)
    LineMain(txt)
    txt.pack(expand='yes')
    root.mainloop()

