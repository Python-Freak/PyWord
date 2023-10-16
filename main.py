import tkinter as tk
import ctypes
from json import loads, dumps
from tkinter.filedialog import askopenfilename, asksaveasfilename
from functools import partial
ctypes.windll.shcore.SetProcessDpiAwareness(True)

def rgb2hex(x):
    r,g,b = x
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

root = tk.Tk()
root.geometry('600x600')

applicationName = 'Rich Text Editor'
root.title(applicationName)

filePath = None
initialdir = '.'
validFileTypes = (
    ("Rich Text File","*.rte"),
)
fontName = 'Bahnschrift'
padding = 20
document = None
defaultContent = {
    "content": "",
    "tags": {
        'bold': [(), ()]
    },
}
tagTypes = {
    'Bold': {'font': f'{fontName} 15 bold'},
    'Italic': {'font': f'{fontName} 15 italic'},
    'Code': {'font': 'Consolas 15', 'background': rgb2hex((200, 200, 200))},

    'Normal Size': {'font': f'{fontName} 15'},
    'Larger Size': {'font': f'{fontName} 25'},
    'Largest Size': {'font': f'{fontName} 35'},
    
    'Highlight': {'background': rgb2hex((255, 255, 0))},
    'Highlight Red': {'background': rgb2hex((255, 0, 0))},
    'Highlight Green': {'background': rgb2hex((0, 255, 0))},
    'Highlight Black': {'background': rgb2hex((0, 0, 0))},
    
    'Text White': {'foreground': rgb2hex((255, 255, 255))},
    'Text Grey': {'foreground': rgb2hex((200, 200, 200))},
    'Text Blue': {'foreground': rgb2hex((0, 0, 255))},
    'Text green': {'foreground': rgb2hex((0, 255, 0))},
    'Text Red': {'foreground': rgb2hex((255, 0, 0))},

}

def resetTags():
    for tag in textArea.tag_names():
        textArea.tag_remove(tag, "1.0", "end")

    for tagType in tagTypes:
        textArea.tag_configure(tagType.lower(), tagTypes[tagType])

def tagToggle(tagName):
    start, end = "sel.first", "sel.last"
    print(textArea.tag_names('sel.first'))
    if tagName in textArea.tag_names('sel.first'):
        textArea.tag_remove(tagName, start, end)
    else:
        textArea.tag_add(tagName, start, end)

def keyDown(event=None):
    root.title(f'{applicationName} - *{filePath}')

def fileManager(event=None, action=None):
    global document, filePath
    if action == 'open':
        filePath = askopenfilename(filetypes=validFileTypes, initialdir=initialdir)
        with open(filePath, 'r') as f:
            document = loads(f.read())
        textArea.delete('1.0', tk.END)
        textArea.insert('1.0', document['content'])
        root.title(f'{applicationName} - {filePath}')
        resetTags()
        for tagName in document['tags']:
            for tagStart, tagEnd in document['tags'][tagName]:
                textArea.tag_add(tagName, tagStart, tagEnd)
    elif action == 'save':
        document = defaultContent
        document['content'] = textArea.get('1.0', tk.END)
        for tagName in textArea.tag_names():
            if tagName == 'sel': continue

            document['tags'][tagName] = []
            ranges = textArea.tag_ranges(tagName)
            for i, tagRange in enumerate(ranges[::2]):
                document['tags'][tagName].append([str(tagRange), str(ranges[i+1])])

            if not filePath:
                newfilePath = asksaveasfilename(filetypes=validFileTypes, initialdir=initialdir)
            if newfilePath is None: return
            filePath = newfilePath
            if not filePath.endswith('.rte'):
                filePath += '.rte'
            with open(filePath, 'w') as f:
                print('Saving at: ', filePath)  
                f.write(dumps(document))
            root.title(f'{applicationName} - {filePath}')

textArea = tk.Text(root, font=f'{fontName} 15', relief=tk.FLAT, undo=True, maxundo= -1, autoseparators=True)
textArea.pack(fill=tk.BOTH, expand=tk.TRUE, padx=padding, pady=padding)
textArea.bind("<Key>", keyDown)

resetTags()

menu = tk.Menu(root)
root.config(menu=menu)

fileMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=fileMenu)

fileMenu.add_command(label="Open", command=partial(fileManager, action='open'), accelerator='Ctrl+O')
root.bind_all('<Control-o>', partial(fileManager, action='open'))

fileMenu.add_command(label="Save", command=partial(fileManager, action='save'), accelerator='Ctrl+S')
root.bind_all('<Control-s>', partial(fileManager, action='save'))

fileMenu.add_command(label="Exit", command=root.quit)

formatMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Format", menu=formatMenu)

for tagType in tagTypes:
    formatMenu.add_command(label=tagType, command=partial(tagToggle, tagName=tagType.lower()))

root.mainloop()

