"""
tkinter app: CodeX2 - A simple code editor
repository link: 
"""

#? Libraries & Modules
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter.colorchooser import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
import ctypes, os

#// None
#? Functionality Code
ctypes.windll.shcore.SetProcessDpiAwareness(True) # make the rendering resolution higher
class CodeX2():
    window = tb.Window(themename="darkly") # creating the window and setting the theme to darkly
    window.resizable(False, False) # making the window non-resizable from the UI
    window.title("CodeX2 - Untitled") # setting the window title

    WIDTH = 1080 # the width of the screen
    HEIGHT = 600 # the height of the screen
    x = int((window.winfo_screenwidth() / 2) - (WIDTH / 2)) # this and the next line of code gets the window to spawn right on the center of the screen
    y = int((window.winfo_screenheight() / 2) - (HEIGHT / 2))
    window.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}') # setting the geometry of the window

    dfFont = ("agave NFM", 12) # a variable with the default font family and size. A good alternative: JetBrains Mono Medium, 10
    dfColor = "#ffffff" # a variable with the default font color
    fileName = None

    syntaxState = False
    size = "1080x600"

    oldPos = ""

    textArea = Text(window, font=(dfFont[0], dfFont[1]), foreground=dfColor, blockcursor=False) # Adding a 'Text' widget to the window
    cmdEntry = tb.Entry(window, font=(dfFont[0], 10), bootstyle="dark")
    def execute(self):
        os.system(self.cmdEntry.get())
        self.cmdEntry.delete(0, END)

    # Adding some tags with different colors assigned to them
    textArea.tag_configure("RED", foreground="#D5667A")
    textArea.tag_configure("GREEN", foreground="#A3BE8C")
    textArea.tag_configure("BLUE", foreground="#61AFEF")
    textArea.tag_configure("PURPLE", foreground="#B48EAD")
    textArea.tag_configure("CYAN", foreground="#56B6C2")
    textArea.tag_configure("YELLOW", foreground="#EBCB8B")

    pList = [
        "print", "input"
    ]

    words = [
        ".",
        "\"", "'",
        "from", "import", "def", "class", "if", "else", "elif", "pass", "break", "continue", "try", "except", "for", "return", "with",
        "*", "\\", "/", "+", "-", "=", "==", "<=", ">=", "<", ">", "!=", "+=", "-=",
        "True", "False", "None", "self"
    ] # a list with all the words the syntax highlighter will have to look for
    # lists and their colors. this is useful when we check if the word found is in the red list or in some other
    redWords = ["."]
    greenWords = ["\"", "'"]
    purpleWords = ["from", "import", "def", "class", "if", "else", "elif", "pass", "break", "continue", "try", "except", "for", "return", "with", "in"]
    cyanWords = ["*", "\\", "/", "+", "-", "=", "==", "<=", ">=", "<", ">", "!=", "+=", "-="]
    yellowWords = ["True", "False", "None", "self"]

    # LINK - addExtensions()
    def addExtensions(self):
        def loadExtensions():
            try:
                for file in os.listdir("extensions/"):
                    fn, ext = file.split(".")
                    if ext == "ext":
                        with open(f"extensions/{file}", "r+") as extensionConfig:
                            for line in extensionConfig.readlines():
                                line = line.removesuffix("\n")
                                try:
                                    varName, varValue = line.split(" = ")
                                    varValue = varValue.removeprefix("\"").removesuffix("\"")
                                except:
                                    varName = line
                                    varValue = ""
                                # font styles
                                if varName == "font.default.family":
                                    self.dfFont = (varValue, self.dfFont[1])
                                    self.textArea.configure(font=self.dfFont)
                                elif varName == "font.default.size":
                                    self.dfFont = (self.dfFont[0], varValue)
                                    self.textArea.configure(font=self.dfFont)
                                # syntaxHighlighting styles
                                elif varName == "syntaxHighlighting.default.mode":
                                    if varValue == "True":
                                        self.toggleHighlighting(False)
                                    else:
                                        pass
                                # window styles
                                elif varName == "window.default.size":
                                    if varValue == "small":
                                        varValue = "1080x600"
                                        self.changeSizeTo(1)
                                    elif varValue == "medium":
                                        varValue = "1240x650"
                                        self.changeSizeTo(2)
                                    else:
                                        varValue = "1600x800"
                                        self.changeSizeTo(3)
                                    self.size = varValue
                                # treeview styles
                                elif varName == "treeview.default.style":
                                    self.treeview.configure(bootstyle=varValue)
                                #settings button styles
                                elif varName == "settingsButton.default.style":
                                    self.settingButton.configure(bootstyle=varValue)
                                # textArea styles
                                elif varName == "textArea.default.foreground":
                                    self.textArea.configure(foreground=varValue)
                                # cmd styles
                                elif varName == "cmdEntry.default.style":
                                    self.cmdEntry.configure(bootstyle=varValue)
                                # open button styles
                                elif varName == "openButton.default.style":
                                    self.openButton.configure(bootstyle=varValue)
                                # save button styles
                                elif varName == "saveButton.default.style":
                                    self.saveButton.configure(bootstyle=varValue)
                                else:
                                    pass
            except:
                ans = askretrycancel("Error", "Couldn't load extensions")
                if ans == True:
                    self.addExtensions()
                else:
                    pass
        loadExtensions()
        self.window.bind('<Alt-e>', func=lambda event: loadExtensions())
    
    # LINK - toggleHighlighting()
    def toggleHighlighting(self, state=None):
        if state == None:
            state = self.syntaxState
            if state == False:
                pass
            elif state == True:
                self.highlight()
            else:
                pass
        else:
            state = self.syntaxState
            if state == False:
                self.highlight()
                state = True
            elif state == True:
                state = False
            else:
                state = False
            self.syntaxState = state
    # Syntax Highlighting Feature
    def check(self,pre, post, preMinusOne, postPlusOne): # creating a function to check if before and after the pattern found, there are any letters
        letters = [
            "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m",
            "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Z", "X", "C", "V", "B", "N", "M"
        ]
        pre = self.textArea.get(pre, preMinusOne) # getting the characters before and after
        post = self.textArea.get(post, postPlusOne)
        # checking
        if pre in letters:
            return False
        if post in letters: # the quick
            return False
        if pre not in letters and post not in letters:
            return True
    def highlight(self): # optimized
        for word in self.words:
            start = 1.0
            currentPos = self.textArea.search(word, start, stopindex=END)
            pos = currentPos.replace(self.oldPos, "")
            while pos:
                length = len(word)
                row, col = pos.split('.')
                end = int(col) + length
                end = row + '.' + str(end)
                pre = row + '.' + str(int(col) - 1)
                preMinusOne = row + '.' + col
                post = row + '.' + str(int(col) + 1)
                postPlusOne = row + '.' + str(int(col) + length + 1)
                if word == ".":
                    self.textArea.tag_add("RED", pos, end)
                elif word == "\"" or word == "'":
                    self.textArea.tag_add("GREEN", pos, end)
                elif self.check(pre, post, preMinusOne, postPlusOne) == True:
                    if word in self.redWords:
                        self.textArea.tag_add("RED", pos, end)
                    elif word in self.redWords:
                        self.textArea.tag_add("GREEN", pos, end)
                    elif word in self.purpleWords:
                        self.textArea.tag_add("PURPLE", pos, end)
                    elif word in self.cyanWords:
                        self.textArea.tag_add("CYAN", pos, end)
                    elif word in self.yellowWords:
                        self.textArea.tag_add("YELLOW", pos, end)
                start = end
                pos = self.textArea.search(word, start, stopindex=END)
    # LINK - addSystemNotification()
    def systemNotification(self, windowMaster, style=DARK, title="System Notification", message="Some Message", duration=3):
        durationInSeconds = duration * 1000
        systemNotification = ToastNotification(title=title, message=message, duration=durationInSeconds, bootstyle=style)
        systemNotification.show_toast()

    # LINK - addItemToTreeview()
    def addItemToTreeview(self, text, value): # a function to add items to the 'Files' treeview (the main treeview)
        self.treeview.insert("", "end", text=text, values=value)
    
    # LINK - removeItemsFromTreeview()
    def removeItemsFromTreeview(self): # a function that deletes all the items from the 'Files' treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
    
    # LINK - updateView()
    def updateView(self): # a function that uses the two functions above combined to update the 'Files' treeview
        self.removeItemsFromTreeview()
        for item in os.scandir("container/"):
            item = str(item).removeprefix("<DirEntry '").removesuffix("'>")
            self.addItemToTreeview("0", item)

    # LINK - addSnippets()
    def addSnippets(self):
        toplevel = tb.Toplevel("Enter Snippet Name") # create a toplevel (secondary window)
        toplevel.resizable(False, False) # make it non-resizable
        WIDTH = 500 # basic WIDTH and HEIGHT
        HEIGHT = 150
        x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2)) # centering it to the middle of the screen
        y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
        toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}') # setting the geometry of the toplevel
        # WIDGETS
        entry = tb.Entry(toplevel, font=("agave NFM", 12), bootstyle="info", width=40) # creating an entry widget
        entry.pack(anchor=N, pady=10) # packing it to the toplevel so its visible
        def snippetEditor(content): # creating a function that the user can add a snippet via UI
            toplevel = tb.Toplevel("Snippet Editor")
            toplevel.resizable(False, False)
            WIDTH = 1000
            HEIGHT = 615
            x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
            y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
            toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
            # WIDGETS
            textArea = Text(toplevel, font=(self.dfFont[0], self.dfFont[1]), foreground=self.dfColor, blockcursor=True)
            textArea.pack(anchor=NW, pady=0, padx=0, expand=True, fill=X)
            def click(content):
                try:
                    with open("snippets/"+content, "w+") as f:
                        f.write(""+ textArea.get("1.0", END))
                        f.close()
                except:
                    ans = askretrycancel("Error", "Couldn't save the snippet named '"+ content +"'")
                    if ans == True:
                        snippetEditor()
                    else:
                        pass
                toplevel.destroy()
            saveButton = tb.Button(toplevel, text="Save", command=lambda:click(content), cursor="hand2", bootstyle="info")
            saveButton.pack(anchor=N, pady=2, expand=True, fill=X)
        def click(): # creating a function that when clicked creates a snippet and then calls the function 'snippetEditor' so the user can add text to the snippet
            content = entry.get() +".txt"
            try:
                with open("snippets/"+content, "w") as f:
                    f.close()
                snippetEditor(content)
                toplevel.destroy()
            except:
                ans = askretrycancel("Error", "Couldn't create the snippet '"+ content.removesuffix(".txt") +"'")
                if ans == True:
                    click()
                else:
                    pass
        button = tb.Button(toplevel, text="Continue", command=click, cursor="hand2", bootstyle="info")
        button.pack(anchor=N, pady=10)

    # LINK - addKeyboardShortcuts()
    def addKeyboardShortcuts(self): # creating a function that adds keyboard shortcuts to the program
        # Run File Feature
        def runFile(): # creating a function that runs a given file
            try:
                os.system("start container/"+self.fileName)
            except:
                ans = askretrycancel("Error", "Couldn't run the file '"+ str(self.fileName) +"'")
                if ans == True:
                    runFile()
                else:
                    pass
        # Snippets Feature
        def insertSnippet(): # creating a function to ask the user for the snippet he wants to add
            def addSnippetsToTreeview():
                for item in os.scandir("snippets/"):
                    item = str(item).removeprefix("<DirEntry '").removesuffix(".txt'>")
                    treeview.insert("", "end", text="0", values=item)
            toplevel = tb.Toplevel("Snippets Menu")
            toplevel.resizable(False, False)
            WIDTH = 500
            HEIGHT = 500
            x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
            y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
            toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
            # WIDGETS
            treeview = tb.Treeview(toplevel, bootstyle="default", columns=0, cursor="crosshair", selectmode="browse", show="headings", height=12)
            treeview.heading("0", None, text="Snippets", anchor=S)
            treeview.pack(anchor=N, pady=2, padx=2, expand=True, fill=X)
            addSnippetsToTreeview()
            selectEntry = tb.Entry(toplevel, font=("agave NFM", 12), bootstyle="info", width=40)
            selectEntry.pack(anchor=N, pady=10)
            def click():
                content = selectEntry.get() +".txt"
                try:
                    with open("snippets/"+content, "r") as f:
                        for line in f.read():
                            self.textArea.insert(END, line)
                            f.close()
                except:
                    ans = askretrycancel("Error", "Couldn't open the snippet '"+ content.removesuffix(".txt") +"'")
                    if ans == True:
                        insertSnippet()
                    else:
                        pass
                toplevel.destroy()
            continueButton = tb.Button(toplevel, text="Continue", command=click, cursor="hand2", bootstyle="info")
            continueButton.pack(anchor=N, pady=10)
            addSnippetButton = tb.Button(toplevel, text="Add Snippet", command=self.addSnippets, cursor="hand2", bootstyle="info-link")
            addSnippetButton.pack(anchor=NW, pady=2, padx=2)
        # Auto Complete Feature
        def autoComplete():
            wordList = self.textArea.get("1.0", END).split(" ")
            wordListLen = len(wordList)
            lastWord = wordList[wordListLen-1].removesuffix("\n")
            if lastWord in self.pList:
                self.textArea.insert(END, "(\"Text\")")
            elif lastWord.endswith(":"):
                self.textArea.insert(END, "\n   ")
        # Functionality Menu
        def functionalityMenu(): # creating a function that within a toplevel displays all the useful shortcuts that the user needs to know (Functionality Menu)
            toplevel = tb.Toplevel("Functionality Menu")
            toplevel.resizable(False, False)
            WIDTH = 500
            HEIGHT = 400
            x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
            y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
            toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
            # WIDGETS
            leftFrame = tb.LabelFrame(toplevel, text="ACTION", bootstyle="info")
            leftFrame.pack(anchor=N, pady=10, padx=5, expand=True, fill=BOTH, side=LEFT)
            rightFrame = tb.LabelFrame(toplevel, text="SHORTCUT", bootstyle="danger")
            rightFrame.pack(anchor=N, pady=8, padx=8, expand=True, fill=BOTH, side=RIGHT)
            def addSection(text, shortcut, commandToExecuteOnClick): # creating a function to make it easier to create sections to the toplevel
                tb.Label(leftFrame, text=text, justify="center", foreground="#ffffff", font=("agave NFM", 12), bootstyle="light").pack(anchor=E, pady=18, padx=40)
                button = tb.Button(rightFrame, text=shortcut, command=commandToExecuteOnClick, cursor="question_arrow", bootstyle="info", width=20)
                button.pack(anchor=N, pady=15, padx=0)
            addSection("Functionality Menu", "Ctrl+F", lambda: functionalityMenu())
            addSection("Run File", "Ctrl+R", lambda: runFile())
            addSection("Insert Snippet", "Ctrl+S", lambda: insertSnippet())
            addSection("Reload extensions", "Alt-E", lambda: self.addExtensions())
        # adding the binding
        self.window.bind('<Control-r>', func=lambda event: runFile())
        self.window.bind('<Control-f>', func=lambda event: functionalityMenu())
        self.window.bind('<Control-s>', func=lambda event: insertSnippet())
        self.window.bind('<space>', func=lambda event: self.toggleHighlighting(None))
        self.window.bind('<\">', func=lambda event: self.toggleHighlighting(None))
        self.window.bind('<Alt-c>', func=lambda event: autoComplete())
    
    # LINK - createNewFile()
    def createNewFile(self):
        toplevel = tb.Toplevel("Enter File Name")
        toplevel.resizable(False, False)
        WIDTH = 500
        HEIGHT = 150
        x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
        y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
        toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
        NewEntry = tb.Entry(toplevel, font=("agave NFM", 12), bootstyle="info", width=40)
        NewEntry.pack(anchor=N, pady=10)
        def click():
            self.fileName = NewEntry.get()
            try:
                with open("container/"+self.fileName, "w+") as f:
                    f.write(""+ self.textArea.get("1.0", END))
                    f.close()
                self.window.title("CodeX2 - "+self.fileName)
            except:
                ans = askretrycancel("Error", "Couldn't create a file named '"+ self.fileName +"'")
                if ans == True:
                    self.createNewFile()
                else:
                    pass
            toplevel.destroy()
            self.updateView()
        NewButton = tb.Button(toplevel, text="Continue", command=click, cursor="hand2", bootstyle="info")
        NewButton.pack(anchor=N, pady=10)
    
    # LINK - openFile()
    def openFile(self):
            toplevel = tb.Toplevel("Enter File Name")
            toplevel.resizable(False, False)
            WIDTH = 500
            HEIGHT = 150
            x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
            y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
            toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
            NewEntry = tb.Entry(toplevel, font=("agave NFM", 12), bootstyle="info", width=40)
            NewEntry.pack(anchor=N, pady=10)
            def click():
                self.fileName = NewEntry.get()
                try:
                    self.textArea.delete("1.0", END)
                    with open("container/"+self.fileName, "r") as f:
                        for line in f.read():
                            self.textArea.insert(END, line)
                            f.close()
                    self.window.title("CodeX2 - "+self.fileName)
                except:
                    ans = askretrycancel("Error", "Couldn't open the file '"+ self.fileName +"'")
                    if ans == True:
                        self.openFile()
                    else:
                        pass
                toplevel.destroy()
                self.updateView()
            NewButton = tb.Button(toplevel, text="Continue", command=click, cursor="hand2", bootstyle="info")
            NewButton.pack(anchor=N, pady=10)
        
    # LINK - settings()
    def changeSizeTo(self, sizeOption):
        smallSize = "1080x600"
        smallSizeX = 1080
        smallSizeY = 600
        mediumSize = "1240x650"
        mediumSizeX = 1240
        mediumSizeY = 650
        largeSize = "1600x800"
        largeSizeX = 1600
        largeSizeY = 800
        if sizeOption == 1:
            self.sizeOption = smallSize
            self.sizeX = smallSizeX
            self.sizeY = smallSizeY
            self.textArea.place(anchor=NE, x=1050, y=20, height=(int(self.window.winfo_screenheight() / 2)-75), width=int(self.window.winfo_screenwidth() / 3)+150)
            self.cmdEntry.place(x=260, y=492, width=int(self.window.winfo_screenwidth() / 3)+150)
            self.openButton.place(anchor=NE, x=643, y=550, height=40, width=(int(self.window.winfo_screenwidth() / 5)))
            self.saveButton.place(anchor=NE, x=1050, y=550, height=40, width=(int(self.window.winfo_screenwidth() / 5)))
        elif sizeOption == 2:
            self.sizeOption = mediumSize
            self.sizeX = mediumSizeX
            self.sizeY = mediumSizeY
            self.textArea.place(anchor=NE, x=1210, y=20, height=(int(self.window.winfo_screenheight() / 2)-28), width=int(self.window.winfo_screenwidth() / 3)+310)
            self.cmdEntry.place(x=260, y=540, width=int(self.window.winfo_screenwidth() / 3)+310)
            self.openButton.place(anchor=NE, x=720, y=600, height=40, width=(int(self.window.winfo_screenwidth() / 4)-20))
            self.saveButton.place(anchor=NE, x=1210, y=600, height=40, width=(int(self.window.winfo_screenwidth() / 4)-20))
        elif sizeOption == 3:
            self.sizeOption = largeSize
            self.sizeX = largeSizeX
            self.sizeY = largeSizeY
            self.textArea.place(anchor=NE, x=1570, y=20, height=(int(self.window.winfo_screenheight() / 2) + 126), width=int(self.window.winfo_screenwidth() / 2)+350)
            self.cmdEntry.place(x=260, y=692, width=int(self.window.winfo_screenwidth() / 2)+350)
            self.openButton.place(anchor=NE, x=900, y=750, height=40, width=(int(self.window.winfo_screenwidth() / 3)))
            self.saveButton.place(anchor=NE, x=1570, y=750, height=40, width=(int(self.window.winfo_screenwidth() / 3)))
        else:
            self.sizeOption = smallSize
            self.sizeX = smallSizeX
            self.sizeY = smallSizeY
            self.textArea.place(anchor=NE, x=1050, y=20, height=(int(self.window.winfo_screenheight() / 2)-75), width=int(self.window.winfo_screenwidth() / 3)+150)
            self.cmdEntry.place(x=260, y=492, width=int(self.window.winfo_screenwidth() / 3)+150)
            self.openButton.place(anchor=NE, x=643, y=550, height=40, width=(int(self.window.winfo_screenwidth() / 5)))
            self.saveButton.place(anchor=NE, x=1050, y=550, height=40, width=(int(self.window.winfo_screenwidth() / 5)))
        self.size = self.sizeOption
        WIDTH = self.sizeX
        HEIGHT = self.sizeY
        x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
        y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
        self.window.geometry(f'{self.size}+{x}+{y}')
    def settings(self):
        def fontChooser():
            def saveFont():
                newFont = fontName.get()
                if newFont == "" or newFont == None:
                    newFont = self.dfFont[0]
                newSize = fontSize.get()
                if newSize == "" or newSize == None:
                    newSize = self.dfFont[1]
                self.dfFont = (newFont, newSize)
                self.textArea.configure(font=(self.dfFont[0], self.dfFont[1]))
                fontlabel.configure(text=self.dfFont[0])
                toplevel.destroy()
            toplevel = tb.Toplevel("Font Settings")
            toplevel.resizable(False, False)
            WIDTH = 500
            HEIGHT = 150
            x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
            y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
            toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
            fontName = tb.Entry(toplevel, font=("agave NFM", 12), bootstyle="info", width=35)
            fontName.pack(anchor=NE, pady=10, padx=10, expand=True, fill=X, side=LEFT)
            fontSize = tb.Entry(toplevel, font=("agave NFM", 12), bootstyle="info")
            fontSize.pack(anchor=NW, pady=10, padx=10, expand=True, fill=X, side=RIGHT)
            saveButton = tb.Button(toplevel, text="Continue", command=saveFont, cursor="hand2", bootstyle="info")
            saveButton.place(anchor=N, x=250, y=90)
        def fontColorChanger():
            self.dfColor = askcolor()[1]
            self.textArea.config(foreground=self.dfColor)
            fontColor.configure(text=self.dfColor)
        def sizeChanger():
            toplevel = tb.Toplevel("Size Settings")
            toplevel.resizable(False, False)
            WIDTH = 500
            HEIGHT = 150
            x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
            y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
            toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
            # widgets
            tb.Button(toplevel, text="Small", command=lambda: self.changeSizeTo(1), bootstyle="success-outline", cursor="hand2").place(x=50, y=50)
            tb.Button(toplevel, text="Medium", command=lambda: self.changeSizeTo(2), bootstyle="warning-outline", cursor="hand2").place(x=200, y=50)
            tb.Button(toplevel, text="Large", command=lambda: self.changeSizeTo(3), bootstyle="danger-outline", cursor="hand2").place(x=370, y=50)
        toplevel = tb.Toplevel("Settings")
        toplevel.resizable(False, False)
        WIDTH = 500
        HEIGHT = 400
        x = int((self.window.winfo_screenwidth() / 2) - (WIDTH / 2))
        y = int((self.window.winfo_screenheight() / 2) - (HEIGHT / 2))
        toplevel.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
        # Font
        leftFrame = tb.LabelFrame(toplevel, text="INFORMATION", bootstyle="info")
        leftFrame.pack(anchor=N, pady=10, padx=5, expand=True, fill=BOTH, side=LEFT)
        rightFrame = tb.LabelFrame(toplevel, text="INTERACT", bootstyle="danger")
        rightFrame.pack(anchor=N, pady=8, padx=8, expand=True, fill=BOTH, side=RIGHT)
        # WIDGETS
        fontlabel = tb.Label(leftFrame, text=self.dfFont[0], font=("agave NFM", 10), bootstyle="info", width=25)
        fontlabel.pack(anchor=N, pady=15, padx=10)
        fontbutton = tb.Button(rightFrame, text="Edit", command=fontChooser, cursor="hand2", bootstyle="danger", width=20)
        fontbutton.pack(anchor=N, pady=10, padx=0)
        # Font color
        fontColor = tb.Label(leftFrame, text=self.dfColor, font=("agave NFM", 10), bootstyle="info", width=25)
        fontColor.pack(pady=15, padx=10)
        fontColorbutton = tb.Button(rightFrame, text="Edit", command=fontColorChanger, cursor="hand2", bootstyle="danger", width=20)
        fontColorbutton.pack(pady=10, padx=0)
        # toggle syntax highlighting
        syntaxLabelStatus = tb.Label(leftFrame, text="Syntax Hlght: "+str(self.syntaxState), font=("agave NFM", 10), bootstyle="info", width=25)
        syntaxLabelStatus.pack(pady=15, padx=10)
        self.toggler = tb.Button(rightFrame, text="Toggle", command=lambda: self.toggleHighlighting(self.syntaxState), bootstyle="danger", cursor="hand2", width=20)
        self.toggler.pack(pady=10, padx=0)
        # size select
        sizeLabel = tb.Label(leftFrame, text="Size: "+str(self.size), font=("agave NFM", 10), bootstyle="info", width=25)
        sizeLabel.pack(pady=15, padx=10)
        sizeButton = tb.Button(rightFrame, text="Edit", command=sizeChanger, bootstyle="danger", cursor="hand2", width=20)
        sizeButton.pack(pady=10, padx=0)

    # LINK - __init__()
    def __init__(self):
        # Making the widgets auto-resizable (within the window)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        # Keyboard Extensions
        self.addKeyboardShortcuts()
        # Treeview
        self.treeview = tb.Treeview(self.window, bootstyle="default", columns=0, cursor="crosshair", selectmode="browse", show="headings")
        self.treeview.heading("0", None, text="Files", anchor=S)
        for item in os.scandir("container/"):
            item = str(item).removeprefix("<DirEntry '").removesuffix("'>")
            self.addItemToTreeview("0", item)
        self.treeview.pack(anchor=NW, pady=20, padx=20, expand=True, fill=Y)
        self.treeview.bind("<Double-1>", func=lambda event: self.createNewFile)
        # settings button
        self.settingButton = tb.Button(self.window, text="Settings", command=self.settings, bootstyle="warning-outline", cursor="hand2", width=23)
        self.settingButton.pack(anchor=NW, pady=10, padx=18)
        # Text Area
        self.textArea.place(anchor=NE, x=1050, y=20, height=(int(self.window.winfo_screenheight() / 2)-75), width=int(self.window.winfo_screenwidth() / 3)+150)
        # CMD entry
        self.cmdEntry.place(x=260, y=492, width=int(self.window.winfo_screenwidth() / 3)+150)
        self.cmdEntry.bind('<Return>', func=lambda event: self.execute())
        # Text Area Buttons
        self.openButton = tb.Button(self.window, text="Open", command=self.openFile, bootstyle="primary-outline", cursor="hand2")
        self.openButton.place(anchor=NE, x=643, y=550, height=40, width=(int(self.window.winfo_screenwidth() / 5)))
        self.saveButton = tb.Button(self.window, text="Save", command=self.createNewFile, bootstyle="primary-outline", cursor="hand2")
        self.saveButton.place(anchor=NE, x=1050, y=550, height=40, width=(int(self.window.winfo_screenwidth() / 5)))
        # loading extensions
        #self.addExtensions()
    def run(self):
        self.window.mainloop()

#? Main Code
CodeX2().run()
