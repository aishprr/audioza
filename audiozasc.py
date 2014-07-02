from Tkinter import *
import Tkinter, tkFileDialog
import pyaudio
import pylab
import numpy
import wave
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkMessageBox import showinfo    
import sys
import copy
import audioop
import time

class Filedata(object):
    
    def __init__(self,file_path):
        #initializes all the values for any new file that is
        # opened. Maximum of 8 files can be opened.
        #Corresponing changes are made in the attributes of
        #each file when any change is made.
        
        self.file_path = file_path
        self.timeElapsed = 0
        self.uploadval = False                                                          
        self.createval = False                                                          
        iofslash = len(file_path)-file_path[::-1].find("/")
        self.filename = file_path[iofslash:]
        self.selectval = False
        self.cutval = False
        self.cutpart = numpy.fromstring("",dtype=numpy.int16)
        self.copyval = False
        self.copypart = numpy.fromstring("",dtype=numpy.int16)
        self.pasteval = False
        self.saveval = False
        self.saveasval = False
        self.removenoiseval = False
        self.amplitudevstimeval = False
        self.powervsfreqval = False
        self.soundTrackArray = numpy.fromstring("",dtype=numpy.int16)
        self.origparameters = ()
        self.tempFile = False
        self.tempFileArray = numpy.fromstring("",dtype=numpy.int16)
        self.tempfileparameters =()
        self.removevoiceval = False
        self.playFile = False
        self.plotcount = 0
        self.sheetmusic =False
        

    def plot(self,app,rate,stage):

        try:
            self.plotcount+=1
            #it is perm if it is permanent that is, if
            #it is the original file or if it is the one saved
            #in memory finally maybe by clicking on save or saveas.
            if(stage == "perm"):
                t = self.soundTrackArray
                CHANNELS = self.origparameters[0]
            elif (stage =="temp"):
                t = self.tempFileArray
                CHANNELS = self.tempfileparameters[0]
            self.amplitudevstimeval = True
            self.powervsfreqval = False
            self.fi = pylab.Figure(figsize=(6.5,5), dpi=100)
            a = self.fi.add_subplot(111)
            if(CHANNELS==2):
                a.plot(numpy.arange(len(t))/(2.0*float(rate)),t,"-r", alpha = 1)
            elif(CHANNELS==1):
                a.plot(numpy.arange(len(t))/float(rate),t,"-r", alpha = 1)
            self.canvas = FigureCanvasTkAgg(self.fi, master=app)
            self.canvas.show()
            self.canvas.get_tk_widget().place(relx = 1.0/3 ,rely =0.125)

        except:
            #If there is a memory overflow error, then this happens
            app.createMessage("Graph Error. File is uploaded!")

    def destroy(self):
        #This function destroys the previously existing graph whenever a
        #new one is drawn in order to clear memory.
        try:
            if(self.plotcount!=0):
                if(self.amplitudevstimeval == True):
                    self.canvas.get_tk_widget().destroy()
                else:
                    self.canvas.get_tk_widget().destroy()
        except:
            pass
            
    def fftplot(self,app,rate,stage):
        try:
            self.plotcount+=1
            if(stage == "perm"):
                t = self.soundTrackArray
                CHANNELS = self.origparameters[0]
            elif (stage =="temp"):
                t = self.tempFileArray
                CHANNELS = self.tempfileparameters[0]
            
            self.amplitudevstimeval = False
            self.powervsfreqval = True
            self.fftfi = pylab.Figure(figsize=(6.5,5), dpi=100)
            a = self.fftfi.add_subplot(111)
            #Performs fft on the values - inbuilt method
            y=numpy.fft.fft(t)
            fftm=10*numpy.log10(abs(y.real))[:len(t)/2]
            freq=numpy.fft.fftfreq(numpy.arange(len(t)).shape[-1])[:len(t)/2]
            a.plot(freq,fftm,"-b", alpha = 1)
            self.canvas = FigureCanvasTkAgg(self.fftfi, master=app)
            self.canvas.show()
            self.canvas.get_tk_widget().place(relx = 1.0/3 ,rely =0.125)
            
        except:
            #In case of memory overflow error.
            app.createMessage("Graph Error. File is uploaded!")
            
class Application(Canvas,Filedata):

    def Upload(self):
        
        if(self.upload["bg"]=="black"):
                self.upload["bg"]="dark green"
                # This gives a dialog box to select the file to upload
                root = Tk()
                root.withdraw()
                file_path = tkFileDialog.askopenfilename()
                count = len(self.openFileList) + 1
                if(count>=8):
                    showinfo("Error","Maximum 8 Files")
                    return
                count-=1
                if(file_path):
                    try:
                        count = len(self.openFileList)+1
                        p = "file"+str(count)
                        # A new class object of Filedata type is created
                        # and assigned to a file named "fileN" where N
                        # is the number of the file starting from 1 among
                        #the files which have been opened till now.
                        execute = "%s = Filedata(file_path)"%(p)
                        exec(execute)
                        oldSelected = self.selectedFile
                        self.createMessage("Uploading...")
                        exec("self.selectedFile = %s"%(p))
                        f = self.selectedFile
                        self.openFileList+=[f]
                        f.uploadval = True
                        self.upload["bg"]= "black"
                        CHUNK = 1024
                        wf = wave.open(file_path,'rb')
                        (nchannels,sampwidth,framerate,nframes,comptype,compname) = wf.getparams()
                        h = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                        f.origparameters = h
                        #All the data is transfered to a string
                        data = wf.readframes(nframes*nchannels)
                        #All data is saved into a numpy array
                        t=numpy.fromstring(data,dtype=numpy.int16)
                        #rate is by default 44100, as it is the most common
                        #one. I will not be dealing with any other rates.
                        rate = 44100
                        f.soundTrackArray = t
                        #Plots the amplitude vs time graph
                        f.plot(self,rate,'perm')
                        self.createMessage("Done!")
                        #makes the file button on top with which it can
                        #be accessed later
                        self.createFileButton(f,count)
                        self.createOpenFiles()
                        self.upload["bg"]= "black"
                    
                    except:
                        #If there is an error, like a memory flow error,
                        # it will not be loaded, and a message is given to the
                        #user.
                        self.openFileList=self.openFileList[:-1]
                        self.selectedFile = oldSelected
                        self.createMessage("Error Loading File")
                                 
                else:
                    self.upload["bg"] = "black"
        else:
            self.upload["bg"]= "black"

    def selectFilePressed(self,name):
        self.createMessage("")
        g = name
        fileNumber = int(g[-1])
        count = 1
        for f in self.openFileList:
            
            if(count==fileNumber):

                if(name=="file1"):
                    self.file1["bg"] = self.sfcolour
                    
                elif(name=="file2"):
                    self.file2["bg"] = self.sfcolour
                    
                elif(name=="file3"):
                    self.file3["bg"] = self.sfcolour
                    
                elif(name=="file4"):
                    self.file4["bg"] = self.sfcolour
                    
                elif(name=="file5"):
                    self.file5["bg"] = self.sfcolour
                    
                elif(name=="file6"):
                    self.file6["bg"] = self.sfcolour
                    
                elif(name=="file7"):
                    self.file7["bg"] = self.sfcolour
                    
                elif(name=="file8"):
                    self.file8["bg"] = self.sfcolour
                    
                if(name!="file1" and len(self.openFileList)>0):
                    
                    self.file1["bg"] = self.nsfcolour
                    
                if(name!="file2" and len(self.openFileList)>1):
                    self.file2["bg"] = self.nsfcolour
                    
                if(name!="file3" and len(self.openFileList)>2):
                    self.file3["bg"] = self.nsfcolour
                    
                if(name!="file4"and len(self.openFileList)>3):
                    self.file4["bg"] = self.nsfcolour
                    
                if(name!="file5"and len(self.openFileList)>4):
                    self.file5["bg"] = self.nsfcolour
                    
                if(name!="file6"and len(self.openFileList)>5):
                    self.file6["bg"] = self.nsfcolour
                    
                if(name!="file7"and len(self.openFileList)>6):
                    self.file7["bg"] = self.nsfcolour
                    
                if(name!="file8"and len(self.openFileList)>7):
                    self.file8["bg"] =self.nsfcolour

                s = "file"+str(count)
                rate = 44100
                self.selectedFile = f
                f.uploadval = True
                self.upload["bg"]= "black"
                #when the file button is pressed, it is opened and the
                #amplitude vs time plot comes up by default.
                if(f.tempFile==True):
                    f.plot(self,rate,"temp")        
                else:
                    f.plot(self,rate,"perm")
            count+=1

    def getSecondsInputAndCreate(self):

        self.s= self.E.get()
        try:
            
            seconds = int(self.s)
            #if a non-integer is entered, it crashes and gives the error message
            if(seconds>0):
                
                self.w.destroy()
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 2
                RATE = 44100
                self.file_opt = options = {}
                options['filetypes'] = [('Wave files', '.wav')]
                options['initialfile'] = 'untitled'
                options['parent'] = self
                file_path = tkFileDialog.asksaveasfilename(**self.file_opt)

                if file_path:
                    
                        self.createMessage("Recording")
                
                        RECORD_SECONDS = seconds
                        WAVE_OUTPUT_FILENAME = file_path
                        p = pyaudio.PyAudio()
                        stream = p.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    input=True,
                                    frames_per_buffer=CHUNK)

                        count = len(self.openFileList)+1
                        s = "file"+str(count)
                        execute = "%s = Filedata(file_path)"%(s)
                        exec(execute)
                        #the file is added to the openFileList
                        exec("self.openFileList+=[%s]"%(s))
                        #It is now the latest file, and hence the selectedFile
                        exec("self.selectedFile = %s"%(s))
                        f = self.selectedFile
                        exec("%s.createval = True"%(s))
                        frames = []
                        t = numpy.fromstring("",dtype=numpy.int16)
                        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                           data = stream.read(CHUNK)
                           frames.append(data)
                           pcm=numpy.fromstring(data, dtype=numpy.int16)
                           t = numpy.append(t,pcm)
                        
                        self.createMessage("Finished recording")
                        #It is directly plotted
                        f = pylab.Figure(figsize=(6.5,5), dpi=100)
                        a = f.add_subplot(111)
                        a.plot(numpy.arange(len(t))/(2*float(RATE)),t,"-r", alpha = 1)
                        canvas = FigureCanvasTkAgg(f, master=self)
                        canvas.show()
                        canvas.get_tk_widget().place(relx = 1.0/3 ,rely =0.125)
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.setnframes = len(numpy.ndarray.tostring(t))
                        wf.setcomptype("NONE","not compressed")
                        wf.writeframes(b''.join(frames))
                        wf.close()
                        self.record["bg"]= "black"
                        exec("self.createFileButton(%s,count)"%(s))
                        #parameters are assigned
                        exec("%s.origparameters = wf.getparams()"%(s))
                        exec("%s.soundTrackArray = t"%(s))
                        self.createOpenFiles()

            else:
                showinfo("Warning!","Enter positive integer for seconds")
                
        except:
            showinfo("Warning!","Enter positive integer for seconds")
                
        
    def Record(self):
        self.createMessage("")
        if(self.record["bg"]=="black"):
            #new window to get number of seconds input.
            self.w = Toplevel(self)
            self.w.title = "Record"
            L = Label(self.w, text="Seconds to Record For")
            L.pack(side = LEFT)
            self.E = Entry(self.w)
            self.E.focus_set()
            self.E.pack(side = RIGHT)
            B = Button(master = self.w, text="Ok, Save and Start Recording", width=10, command=self.getSecondsInputAndCreate)
            B.grid(row = 3, column = 0)
            self.record["bg"]= "dark green"
            
        else:
            self.record["bg"]= "black"

    def selectUsingBounds(self):
        
        self.inputInit = self.E3.get()
        self.inputFin = self.E4.get()

        try:
            
            self.initTime = float(self.inputInit)
            self.finTime = float(self.inputFin)
            #crashes if there is any non-float value entered.
            if(self.initTime>=0 and self.finTime>=0):

                f = self.selectedFile
                self.createMessage("Getting data...")
                if(f.tempFile==True):
                    nframes = f.tempfileparameters[3]
                    t = f.tempFileArray
                    CHANNELS = f.tempfileparameters[0]
                else:
                    nframes = f.origparameters[3]
                    t = f.soundTrackArray
                    CHANNELS = f.origparameters[0]

                RATE = 44100
                totalDuration = float(nframes)/RATE
                CHUNK = 1024
                        
                if(self.finTime>totalDuration):
                    showinfo("Warning!","Enter Ending Time less than total duration which is %f"%(totalDuration))
                    return

                elif(self.finTime<self.initTime):
                    showinfo("Warning!","Enter Ending Time greater than Stating Time")
                    return
                
                self.w4.destroy()
                
                initialFrame = int((self.initTime/totalDuration)*nframes*CHANNELS)
                finishingFrame = int((self.finTime/totalDuration)*nframes*CHANNELS)

                self.selectedPart = {}
                self.selectedPart["part"]=t[initialFrame:finishingFrame]
                self.selectedPart["channels"] = CHANNELS
                self.selectedPart["init"]=initialFrame
                self.selectedPart["fin"]=finishingFrame

                self.select["bg"]="black"
                f.selectval = True
                self.createMessage("Selected!")
                
            else:
                showinfo("Warning!","Enter positive values only!")
        except:
            showinfo("Warning!","Enter positive numbers only!")

    def Select(self):
        
        self.createMessage("")
        if(self.select["bg"]=="black"):
            self.select["bg"]= "dark green"
            f = self.selectedFile
            if(f==None):
                showinfo("Warning!","Please upload or create a file first")
                self.select["bg"]= "black"
                return
            #new window to get time bounds from user.
            self.w4 = Toplevel(self)
            self.w4.title = "Select"
            L3 = Label(self.w4,text="Starting Time")
            L3.grid(row = 0, column = 0)
            self.E3 = Entry(self.w4)
            self.E3.grid(row = 0, column = 10)
            self.E3.focus_set()
            L4 = Label(self.w4,text="Ending Time")
            L4.grid(row = 3,column = 0)
            self.E4 = Entry(self.w4)
            self.E4.grid(row = 3, column = 10)   
            B1 = Button(master = self.w4, text="Ok, Select", width=10, command=self.selectUsingBounds)
            B1.grid(row = 10, column = 5)
        else:
            self.select["bg"]= "black"


    def Copy(self):

        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            showinfo("Warning!","Please upload or create a file first")
            self.select["bg"]= "black"
            return
            
        if(self.copy["bg"]=="black"):
            if(f.selectval == False):
                self.Select()
            self.copy["bg"]= "dark green"
            self.createMessage("Copying...")
            self.copyCutPart  = self.selectedPart
            f.copyval = True
            self.copy["bg"]= "black"
            self.createMessage("Copied!")

        else:
            self.copy["bg"]= "black"
        
    def Cut(self):
        
        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            showinfo("Warning!","Please upload or create a file first")
            self.select["bg"]= "black"
            return

        if(self.cut["bg"]=="black"):
            if(f.selectval == False):
                self.Select()
            else:
                self.cut["bg"]= "dark green"
                self.copyCutPart  = self.selectedPart
                self.createMessage("Cutting...")
                
                f = self.selectedFile
                rate = 44100
                if(f.tempFile==True):
                    t = f.tempFileArray
                    init = self.copyCutPart["init"]
                    fin = self.copyCutPart["fin"]
                    t = numpy.append(t[0:init],t[fin:])
                    f.tempFileArray = t
                    (nchannels,sampwidth,framerate,nframes,comptype,compname) = f.tempfileparameters 
                    nframes =  len(t)
                    f.tempfileparameters = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                    f.plot(self,rate,"temp")
                else:
                    t = f.soundTrackArray
                    init = self.copyCutPart["init"]
                    fin = self.copyCutPart["fin"]
                    t = numpy.append(t[0:init],t[fin:])
                    f.tempFile = True
                    #if not edit has been made till now, then temp file must
                    #be created at this point
                    f.tempFileArray=t
                    f.tempfileparameters = f.origparameters
                    (nchannels,sampwidth,framerate,nframes,comptype,compname) = f.tempfileparameters 
                    nframes =  len(t)
                    f.tempfileparameters = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                    f.plot(self,rate,"temp")

                f.cutval = True
                self.cut["bg"]= "black"
                self.createMessage("Done cutting!")
        else:
            self.copy["bg"]= "black"
            
    def pasteUsingPosn(self):

        self.inputTime = self.E5.get()

        try:
            self.atTime = float(self.inputInit)

            if(self.atTime>=0):

                f = self.selectedFile
                self.createMessage("Processing...")
                if(f.tempFile==True):
                    nframes = f.tempfileparameters[3]
                    t = f.tempFileArray
                    CHANNELS = f.tempfileparameters[0]
                else:
                    nframes = f.origparameters[3]
                    t = f.soundTrackArray
                    CHANNELS = f.origparameters[0]

                RATE = 44100
                totalDuration = float(nframes)/RATE
                CHUNK = 1024
                        
                if(self.atTime>totalDuration):
                    #Warning given, but user can still enter in the active field.
                    showinfo("Warning!","Enter At Time less than total duration which is %f"%(totalDuration))
                    return

                elif(CHANNELS!=self.copyCutPart["channels"]):
                    showinfo("Warning!","Number of channels of copied/cut part and file to be pasted to must be the same")
                    self.w5.destroy()
                    return
                
                self.w5.destroy()
                self.atFrame = int((self.atTime/totalDuration)*nframes*CHANNELS)
                f = self.selectedFile
                rate = 44100
                if(f.tempFile==True):
                    t = f.tempFileArray
                    part = self.copyCutPart["part"]
                    k = numpy.append(t[0:self.atFrame],part)
                    p = numpy.append(k,t[self.atFrame+1:])
                    #Here, the functions use corresponding array indices to edit.
                    f.tempFileArray = p
                    (nchannels,sampwidth,framerate,nframes,comptype,compname) = f.tempfileparameters 
                    nframes =  len(p)
                    f.tempfileparameters = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                    f.plot(self,rate,"temp")
                else:
                    t = f.soundTrackArray
                    part = self.copyCutPart["part"]
                    k = numpy.append(t[0:self.atFrame],part)
                    p = numpy.append(k,t[self.atFrame+1:])
                    f.tempFile = True
                    f.tempFileArray=p
                    f.tempfileparameters = f.origparameters
                    (nchannels,sampwidth,framerate,nframes,comptype,compname) = f.tempfileparameters 
                    nframes =  len(p)
                    f.tempfileparameters = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                    f.plot(self,rate,"temp")

                
                self.paste["bg"]= "black"
            else:
                showinfo("Warning!","Enter positive values only!")
                self.paste["bg"]= "dark green"
        except:
            showinfo("Warning!","Enter positive numbers only!")
            self.paste["bg"]= "black"

        
    def Paste(self):
        
        self.createMessage("")
        if(self.paste["bg"]=="black"):
            self.paste["bg"]= "dark green"
            f = self.selectedFile
            if(f==None):
                showinfo("Warning!","Please upload or create a file first")
                self.paste["bg"]= "black"
                return
            elif(self.copyCutPart=={}):
                showinfo("Warning!","Please copy or cut from a file first")
                self.paste["bg"]= "black"
                return
            #new window to get at time bounds
            self.w5 = Toplevel(self)
            self.w5.title = "Paste"
            L5 = Label(self.w5,text="Insert at time")
            L5.grid(row = 0, column = 0)
            self.E5 = Entry(self.w5)
            self.E5.focus_set()
            self.E5.grid(row = 0, column = 10)
            B = Button(master = self.w5, text="Ok", width=10, command=self.pasteUsingPosn)
            B.grid(row = 10, column = 5)
            
        else:
            self.paste["bg"]= "black"


    def Save(self):

        self.createMessage("")
        if(self.openFileList !=[]):
            f = self.selectedFile
        
            if(f.saveval ==False):
                self.save["bg"]= "dark green"
                f.saveval = True
                if(f.tempFile==True):
                        t = f.tempFileArray
                        u = f.tempfileparameters
                else:
                        t = f.soundTrackArray
                        u = f.origparameters
                    
                f.soundTrackArray = t
                f.origparameters = u
                
                WAVE_OUTPUT_FILENAME = f.file_path
                data = numpy.ndarray.tostring(t)
                frames = []
                frames.append(data)
                wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                wf.setparams(u)
                wf.writeframes(b''.join(frames))
                wf.close()
                self.createMessage("Saved!")
                self.save["bg"]="black"

    def Saveas(self):
        
        self.createMessage("")
        if(self.openFileList !=[]):
            f = self.selectedFile
        
            if(f.saveasval ==False):
                f.saveasval = True
                self.saveas["bg"]= "dark green"
                FORMAT = pyaudio.paInt16
                RATE = 44100
                
                self.file_opt = options = {}
                options['filetypes'] = [('Wave files', '.wav')]
                options['initialfile'] = 'untitled'
                options['parent'] = self
                
                file_path = tkFileDialog.asksaveasfilename(**self.file_opt)
                if file_path:
                    f.file_path = file_path
                    WAVE_OUTPUT_FILENAME = f.file_path
                    if(f.tempFile==True):
                        t = f.tempFileArray
                    else:
                        t = f.soundTrackArray
                    data = numpy.ndarray.tostring(t)
                    
                    frames = []
                    frames.append(data)
                    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                    if(f.tempFile):
                        wf.setnchannels(f.tempfileparameters[0])
                        wf.setsampwidth(f.tempfileparameters[1])
                    else:
                        wf.setnchannels(f.origparameters[0])
                        wf.setsampwidth(f.origparameters[1])
                        
                    wf.setframerate(RATE)
                    wf.setnframes = len(t)
                    wf.setcomptype("NONE","not compressed")
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    self.saveas["bg"]= "black"
                else:
                    f.saveasval = False

                f.saveasval = True
                
                self.saveas["bg"]= "black"
            
    def Removevoice(self):
        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            showinfo("Warning!","Please upload or create a file first")
            return
        
        if(f.removevoiceval==False):
            rate = 44100
            self.removevoice["bg"]= "dark green"
            wf = wave.open(f.file_path)
            data = numpy.fromstring(wf.readframes(wf.getnframes()),
                        dtype=numpy.int16)
            CHANNELS = wf.getnchannels()
            if(CHANNELS!=2):
                showinfo("Warning!", "File must be Stereo and not Mono")
                self.removevoice["bg"]= "black"

            else:
                f.tempFile = True
                self.createMessage("Processing...")
                #Each channel is saved alternately and hence, this idea
                # can be used in conjunction with the fact that voice
                #samples are generally present in all channels to eliminate
                # the voice. Here, I use stereo, and hence the below method.
                f.tempVoiceRemovedMono = data[0::2] - data[1::2]
                f.tempVoiceRemovedStereo = audioop.tostereo(f.tempVoiceRemovedMono, 2, 1, 1)
                f.tempFileArray = numpy.fromstring(f.tempVoiceRemovedStereo,dtype=numpy.int16)
                f.removevoiceval = True
                self.createMessage("Done!")
                (nchannels,sampwidth,framerate,nframes,comptype,compname) = (2,2,44100,
                                                                                 len(f.tempVoiceRemovedStereo),
                                                                                 "NONE", "not compressed")
                f.tempfileparameters = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                wf.close()
                f.destroy()
                f.plot(self,rate,'temp')
                self.removevoice["bg"]= "black"
                    
        else:
            self.removevoiceval = True
            self.removevoice["bg"]= "black"

    def getNoiseInputAndFilter(self):

        self.inputHigh= self.E1.get()
        self.inputLow = self.E2.get()
        self.removenoise["bg"]= "dark green"

        try:
            self.highPass = int(self.inputHigh)
            self.lowPass = int(self.inputLow)
            if(self.highPass>=0 and self.lowPass>=0):

                self.w2.destroy()
                f = self.selectedFile
                rate = 44100
                
                if(f.tempFile==True):
                    t = f.tempFileArray
                    CHANNELS = f.tempfileparameters[0]
                    sw = f.tempfileparameters[1]
                else:
                    t = f.soundTrackArray
                    CHANNELS = f.origparameters[0]
                    sw = f.origparameters[1]

                self.createMessage("Processing...")
                ####http://rsmith.home.xs4all.nl/miscellaneous/filtering-a-sound-recording.html
                  
                if(CHANNELS==2):
                    lchannel = t[0::2]
                    rchannel = t[1::2]
                    #uses fft to get frequency data which is arranged in
                    #increasing order, and removes unwanted frequencies using
                    #simple index openrations of numpy ndarrays.
                    lf, rf = numpy.fft.rfft(lchannel), numpy.fft.rfft(rchannel)
                    lf[:self.lowPass], rf[:self.lowPass] = 0, 0 # low pass filter
                    lf[55:66], rf[55:66] = 0, 0 # line noise
                    lf[self.highPass:], rf[self.highPass:] = 0,0 # high pass filter
                    nl, nr = numpy.fft.irfft(lf), numpy.fft.irfft(rf)
                    ns = numpy.column_stack((nl,nr)).ravel().astype(numpy.int16)
                    f.tempFileArray = numpy.fromstring(ns,dtype=numpy.int16)
                    f.removenoiseval = True
                    (nchannels,sampwidth,framerate,nframes,comptype,compname) = (2,sw,44100,len(numpy.ndarray.tostring(ns)),
                                                                                 "NONE", "not compressed")
                    f.tempfileparameters = (nchannels,sampwidth,framerate,nframes,comptype,compname)
                    f.tempFile = True

                if(f.amplitudevstimeval ==True):
                    f.destroy()
                    f.plot(self,rate,'temp')
                else:
                    f.destroy()
                    f.fftplot(self,rate,'temp')
                self.createMessage("Done!")
                self.removenoise["bg"]= "black"
               
            else:
                showinfo("Warning!","Enter positive integer for both frequencies")

        except:
            showinfo("Warning!","Enter positive integer for both frequencies")
        self.removenoise["bg"]= "black"        
                

    def Removenoise(self):

        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            showinfo("Warning!","Please upload or create a file first")
            return 
        if(self.removenoise["bg"]== "black"):
            self.removenoise["bg"]= "dark green"
        
            if(f.tempFile==True):
                t = f.tempFileArray
                CHANNELS = f.tempfileparameters[0]
            else:
                t = f.soundTrackArray
                CHANNELS = f.origparameters[0]
            
            if(CHANNELS==1):

                showinfo("Warning!", "File must be stereo and not mono")
                self.removenoise["bg"]= "black"
                return
            
            elif(CHANNELS ==2):
                lchannel = t[0::2]
                rchannel = t[1::2]
                lf, rf = numpy.fft.rfft(lchannel), numpy.fft.rfft(rchannel)
                maximumvalue = max(len(lf), len(rf))
                minimumvalue = 0
                self.w2 = Toplevel(self)
                self.w2.title = "Filters"
                L1 = Label(self.w2,text="Remove freq higher than (Hz)")
                L1.grid(row = 0, column = 0)
                self.E1 = Entry(self.w2)
                self.E1.grid(row = 0, column = 5)
                self.E1.focus_set()
                L2 = Label(self.w2,text="Remove freq lower than (Hz)")
                L2.grid(row = 3,column = 0)
                self.E2 = Entry(self.w2)
                self.E2.grid(row = 3, column = 5)
                L6 = Label(self.w2,text="Present Highest = %0.2f"%(maximumvalue))
                L6.grid(row = 5, column = 0)
                L7 = Label(self.w2,text="Present Lowest = %0.2f"%(minimumvalue))
                L7.grid(row = 5, column = 5)
                B = Button(master = self.w2, text="Ok", width=10, command=self.getNoiseInputAndFilter)
                B.grid(row = 10, column = 2)
                self.removenoise["bg"]= "black"

        else:
            self.removenoiseval = True
            self.removenoise["bg"]= "black"

    def Amplitudevstime(self):
        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            self.amplitudevstime["bg"]=="dark green"
            showinfo("Warning!","Please upload or create a file first")
            self.amplitudevstime["bg"]=="black"
            return          
        if(self.amplitudevstime["bg"]=="black"):
            
            self.amplitudevstime["bg"]= "dark green"
            self.powervsfreq["bg"]= "black"
            rate = 44100
            f.destroy()
            if(f.tempFile==True):
                f.plot(self,rate,"temp")      
            else:
                f.plot(self,rate,"perm")

        else:
            self.amplitudevstime["bg"]= "black"
            
            

    def Powervsfreq(self):
        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            self.powervsfreq["bg"]= "dark green"
            showinfo("Warning!","Please upload or create a file first")
            self.powervsfreq["bg"]= "black"
            return
        
        if(self.powervsfreq["bg"]=="black"):
            self.powervsfreq["bg"]= "dark green"
            self.amplitudevstime["bg"]= "black"
            f = self.selectedFile
            rate = 44100
            f.destroy()
            if(f.tempFile==True):
                f.fftplot(self,rate,"temp")   
            else:
                f.fftplot(self,rate,"perm")
        else:
            self.powervsfreq["bg"]= "black"
            

    def Sheetmusic(self):
        
        self.createMessage("")
        if(self.sheetmusic["bg"]=="black"):
            self.sheetmusic["bg"]= "dark green"

            
            CHUNK = 1024
            freqList = []
            f = self.selectedFile
            f.sheetmusic = True
            self.Removenoise
            RATE = 44100
            # use a Blackman window
            window = numpy.blackman(CHUNK)
            wf = wave.open(f.file_path, 'rb')
            swidth = wf.getsampwidth()

            if(wf.getparams()[0]!=1):
                showinfo("Warning!","File must be Mono and not Stereo")
                self.sheetmusic["bg"]= "black"
                return

            else:
                data = wf.readframes(CHUNK)
                
                counter = 1
                
                while(data!=''):

                    A3freq = 220
                    A5freq = 880
                    #### FREQUENCY DETECTION FROM http://stackoverflow.com/questions/4431481/frequency-detection-from-a-sound-file
                    
                    # Take the fft and square each value
                    fftData=abs(numpy.fft.rfft(numpy.fromstring(data,dtype=numpy.int16)))**2
                    # find the maximum
                    which = fftData[1:].argmax() + 1
                    # use quadratic interpolation around the max
                    if (which != len(fftData)-1):
                        try:
                            y0,y1,y2 = numpy.log(fftData[which-1:which+2:])
                            x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
                            # find the frequency and output it
                            thefreq = (which+x1)*RATE/CHUNK
                            if(thefreq>=A3freq and thefreq<A5freq):
                                freqList+=[thefreq]
                        except:
                            pass
                            
                    else:
                        thefreq = which*RATE/CHUNK
                        if(thefreq>=A3freq and thefreq<A5freq):
                            freqList+=[thefreq]
                            
                    # read some more data
                    
                    data = wf.readframes(CHUNK)
                    counter+=1

            self.drawList = self.makeListToDraw(freqList)
            self.drawManuscript()
            self.sheetmusic["bg"]= "black"
            
        else:
            self.sheetmusic["bg"]= "black"

        
    def makeListToDraw(self,freqList):
        #Uses valsPerPlot number of frequencied=s to take average
        valsPerPlot = 5
        drawList = []
        for counter in xrange(0,len(freqList), valsPerPlot):
            
            L = []
            for value in xrange(valsPerPlot):
                if((counter+value)<len(freqList)):
                    L+=[freqList[counter+value]]
                else:
                    break
            finalVal = sum(L)/(value+1)
            drawList+=[finalVal]
        return drawList

        
    def noteNo(self,freq):
        #frequency changes by a octaves exponentially.
        #Each note in consecutive octaves has double the
        #frequency of its previous octave.
        import math  
        for no in xrange(88):
            f = 2**((no-40)/12.0) * 261.6
            if (abs(freq - f)<=10):
                return no
        return int(12*math.log((freq/261.6),2)+40)

    def drawNotes(self,drawList,c):

        self.manu["distBetNotes"] = 20
        self.manu["numberNotesPerLine"] = 40
        countNotes = 0
        line = 1
        #Note numbers of all the black notes(considering all as sharps)
        #between A3 and A5
        sharpList = [38,41,43,46,48,50,53,55,58,60]
        for freq in drawList:
            isSharp = False
            N = self.noteNo(freq)
            if(N in sharpList):
                isSharp = True
                N=N-1
            sharpCount = 0
            for i in xrange(len(sharpList)):
                if(sharpList[i]<N):
                    sharpCount+=1
                
            middleCPosn = line*(self.manu["distBetLines"] + self.manu["distBetParts"]*5)
            cx = (countNotes%self.manu["numberNotesPerLine"])*self.manu["distBetNotes"] + self.manu["x0"]
            cy = middleCPosn-(N-40-sharpCount)*(self.manu["distBetParts"]/2.0)
            c.create_oval(cx-4,cy-(self.manu["distBetParts"])/2.0,cx+4,cy+(self.manu["distBetParts"])/2.0, fill="black")
            if(N>=51):
                c.create_line(cx-4,cy,cx-4,cy+(self.manu["distBetParts"])/2.0+20)
            elif(N<51):
                c.create_line(cx+4,cy,cx+4,cy+(self.manu["distBetParts"])/2.0-20)

            if(isSharp==True):
                #creates the sharp symbol
                vl1x = cx - 8
                vl2x = cx - 6
                vly1 = cy - 4
                vly2 = cy + 4
                hlx1 = cx - 10
                hlx2 = cx - 4
                hl1y = cy - 2
                hl2y = cy + 2
                c.create_line(vl1x,vly1,vl1x, vly2)
                c.create_line(vl2x,vly1,vl2x, vly2)
                c.create_line(hlx1,hl1y,hlx2,hl1y)
                c.create_line(hlx1,hl2y,hlx2,hl2y)
                
            countNotes+=1
            
            if(countNotes%self.manu["numberNotesPerLine"]==0):
                line+=1

    def drawManuscript(self):
        self.manu = {}
        self.manu["width"] = 800
        self.manu["height"] = 650
        w = Toplevel(master = self.master)
        w.title = "Rough Manuscript"
        c = Canvas(w, width = self.manu["width"], height = self.manu["height"])
        c.pack()
        self.manu["maxLines"] = 12
        self.manu["eachLine"] = 5
        self.manu["x0"] = 10
        self.manu["y0"] = 20
        self.manu["x1"] = self.manu["width"] - self.manu["x0"]
        self.manu["y1"] = self.manu["y0"]
        self.manu["distBetParts"] = 6
        self.manu["distBetLines"] = 20
        x0 = self.manu["x0"]
        y0 = self.manu["y0"]
        x1 = self.manu["x1"]
        y1 = self.manu["y1"]
        
        for counter in xrange(self.manu["maxLines"]):

            for line in xrange(self.manu["eachLine"]):
                
                c.create_line(x0,y0,x1,y1)
                y0+=self.manu["distBetParts"]
                y1+=self.manu["distBetParts"]
                
            y0+=self.manu["distBetLines"]
            y1+=self.manu["distBetLines"]

        self.drawNotes(self.drawList, c)

    def Help(self):
        self.w6 = Toplevel(self)
        self.w6.title = "Help"
        
        L = Label(self.w6, text="\n\
                This software allows the user to analyze and edit audio files in the .wav format.\n\
                Options available include -\n\
                1. Upload - To upload a file that already exists in any directory, click on the button, browse and select your file.\n\
                2. Record - To record a new file using the default mic of your computer system click on this button, enter the number of seconds and start.\n\
                3. Select - To select a part of a file by entering time limits (easier if you use the amplitidevstime button to get the time limits.)\n\
                4. Copy/Cut - To copy or cut an already selected part if it exists or to select and then copy that part from the selected file from the tabs.\n\
                5. Paste - To paste a copied/cut part to a particular time position of the selected file.\n\
                6. Save/SaveAs - To either save to the existing file or save to a new file respectively.\n\
                7. Removevoice - To remove voice from a stereo audio sample (works well for professionally recorded music.)\n\
                8. Removenoise - To remove noise from a stereo audio sample by giving high and low limit frequencies.\n\
                9. Amplitudevstime - Gives the amplitude vs time (s) graph of the audio to give an indication of variation of sound.\n\
                10. Powervsfreq - Gives the power vs freq graph of the audio (Hz * 10**-4)\n\
                11. Sheetmusic - Gives an approximate note plotting of notes between the notes A3 and A5 on Treble Clef without any rythm analysis for mono sound.\n\
                12. Help - Here you are! :D \n\
                Note1 : Upto 8 audio files can be uploaded at a time!\n\
                Note2 : Stereo means audio data for both channels (left and right speakers) is present, whereas mono means, data is present in a mixed form.\n",justify = LEFT)
        L.pack(side = TOP)
             
    def playSelectedFile(self):
        self.createMessage("")
        f = self.selectedFile
        if(f==None):
            return
        
        if(f.tempFile== True):
            stage = "temp"
        else:
            stage = "perm"

        if(stage == "perm"):

                def callback(in_data, frame_count, time_info, status):
                    f = self.selectedFile   
                    data = wf.readframes(CHUNK)
                    if(data != ''):
                        f.timeElapsed = wf.tell()/float(wf.getframerate())
                        f.framesElapsed = wf.tell()
                        
                    return (data, pyaudio.paContinue)
                
                t = f.soundTrackArray
                self.playing = True
                f.playFile = True
                wf = wave.open(f.file_path,'rb')
                k = pyaudio.PyAudio()
                CHUNK = 1024
                stream = k.open(format=k.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(), output = True,stream_callback = callback)

                while stream.is_active():
                    time.sleep(0.1)
                    
                stream.stop_stream()
                stream.close()
                k.terminate()
                self.playFile = False
        else:

            RATE = 44100
            t = f.tempFileArray
            CHANNELS = 2
            data = numpy.ndarray.tostring(t)
                
            k = pyaudio.PyAudio()
            stream = k.open(format=pyaudio.paInt16,
                                channels=CHANNELS,
                                rate=RATE, output = True)
            self.playing = True
            f.playFile = True
            CHUNK = 1024
            d = data[0: CHUNK]
            counter = 1
            while(d!=''):
                f.framesElapsed = counter*CHUNK
                f.timeElapsed = f.framesElapsed/float(RATE)
                d = data[counter*CHUNK: (counter+1)*CHUNK]
                stream.write(d)
                counter+=1

            stream.stop_stream()
            stream.close()
            k.terminate()
            f.playFile = False

    
    def createPlayButton(self):
        self.playing = False
        self.play = Button(self)
        self.play['text'] = "Play"
        self.play['width'] = 44
        self.play['height'] = 5
        self.play['anchor'] = CENTER
        self.play['bg'] = self.rgbString(0,134,139)
        self.play['fg'] = 'white'
        x = 1.0/3
        y = 7.0/8
        self.play.place(relx=x,rely=y, anchor=NW)
        self.play['command'] = lambda :self.playSelectedFile()

    def createFileButton(self,f,count):

        name = "file"+str(count)
        total = len(self.openFileList)
        if(name=="file1"):
            self.file1 = Button(self)
            v = self.file1
        if(name=="file2"):
            self.file2 = Button(self)
            v = self.file2
        if(name=="file3"):
            self.file3 = Button(self)
            v = self.file3
        if(name=="file4"):
            self.file4 = Button(self)
            v = self.file4
        if(name=="file5"):
            self.file5 = Button(self)
            v = self.file5
        if(name=="file6"):
            self.file6 = Button(self)
            v = self.file6
        if(name=="file7"):
            self.file7 = Button(self)
            v = self.file7
        if(name=="file8"):
            self.file8 = Button(self)
            v = self.file8

        v['text'] = "%s" %(f.filename)
        v['width'] = 11
        v['height'] = 5
        v['anchor'] = CENTER
        if(f==self.selectedFile):
            v['bg'] = self.sfcolour
        else:
            v['bg'] = self.nsfcolour
        v['fg'] = 'white'
        x = 1.0/3 + (2.0*(count-1)/(3.0* 8))
        v.place(relx=x,rely=0, anchor=NW)
        v['command'] = lambda: self.selectFilePressed(name)

    def rgbString(self,red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)

    def createOpenFiles(self):
        count = 0
        for f in self.openFileList:
            count+=1
            self.createFileButton(f,count)

    def createButton(self,t):

        #common function for all the buttons on the left side, and
        #hence so many exec statements.
        fn = t[0].upper()+t[1:]
        exec("self.%s = Button(self)" %(t))
        exec("self.%s['text'] = '%s'" %(t,fn))
        exec("self.%s['width'] = 22" %(t))
        exec("self.%s['height'] = 6" %(t))
        exec("self.%s['anchor'] = CENTER" %(t))
        exec("self.%s['bg'] = 'black'" %(t))
        exec("self.%s['fg'] = 'white'" %(t))
        exec("self.%s['command'] = self.%s" %(t,fn))
        if(self.count%2==1):
            x = 1.0/6
        else:
            x = 0
        exec("self.%s.place(relx=x,rely= (self.count/2)*1.0/7, anchor=NW)"%(t))
        self.count+=1

    def createMessage(self, t):
        self.time = Label(self, font = "Times 21 bold")
        self.time["text"] = t
        self.time["width"] = 20
        self.time['height'] = 4
        self.time["justify"] = "center"
        x = 2.0/3
        y = 6.0/7
        self.time.place(relx = x, rely = y, anchor = NW)
    
    def createWidgetsForSelFile(self):

        self.count=0
        self.createMessage("***WELCOME!***")
        self.createPlayButton()
        self.createButton("upload")
        self.createButton("record")
        self.createButton("select")
        self.createButton("copy")
        self.createButton("cut")
        self.createButton("paste")
        self.createButton("save")
        self.createButton("saveas")
        self.createButton("removevoice")
        self.createButton("removenoise")
        self.createButton("amplitudevstime")
        self.createButton("powervsfreq")
        self.createButton("sheetmusic")
        self.createButton("help")
        
    def timerFired(self):
    
        f = self.selectedFile
        if(f!=None):
            if(f.amplitudevstimeval==True):
                self.amplitudevstime["bg"]= "dark green"
                self.powervsfreq["bg"]= "black"
            
            elif(f.powervsfreqval==True):
                self.amplitudevstime["bg"]= "black"
                self.powervsfreq["bg"]= "dark green"
        try:
            if(self.w.winfo_exists()==False):
                    self.record["bg"]= "black"

        except:
            pass

        delay = 300    
        self.master.after(delay, self.timerFired)
    

    def __init__(self, width, height,master=None):

        self.master = master
        self.width = width
        self.height = height
        Canvas.__init__(self,master,width=self.width ,height=self.height)
        self.pack()
        self.selected = False
        self.openFileList = []
        self.copyCutPart = {}
        self.selectedFile = None
        self.sfcolour = self.rgbString(165,42,42)
        self.nsfcolour = self.rgbString(168,168,168)
        self.createWidgetsForSelFile()
        master.update()
        showinfo("Welcome!", "You may start by either uploading a .wav file of your choice, or creating a new one!")
        self.timerFired()
        
def run():

    root = Tk()
    root.resizable(width = False, height = False)
    app = Application(1000,700,root)
    app.mainloop()

run()
