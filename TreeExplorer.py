# GenoMap Tree Explorer
# Damian Magill 2023

# Module Imports
# System Functions
import sys
#Tree Exploration Imports
from ete3 import Tree, TreeStyle, NodeStyle, AttrFace, TreeNode, RectFace, TextFace, ProfileFace
#Data processing
import pandas as pd
import openpyxl
#Interface Creation
import tkinter as tk
from tkinter import filedialog, simpledialog
import tkinter.scrolledtext as tkst
from tkinter import PhotoImage
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk

from tkinter import ttk

class Application(tk.Frame, tk.Text):
    """ GUI application enabling the labelling and exploration of phylogenetic trees based on genogroup file information"""
    # Class inheriting from tkinter to build GUI around ete3 toolkit functionality
    def __init__(self, master):
        """ Initialize Frame. """
        super(Application, self).__init__(master)
        self.grid()
        self.create_widgets()

        self.subList: list = []  # Subsetting list for labels
        self.strainList: list = [] # Strain selection
        self.reference: dict = {} # Allows to retrieve strains from labels
        self.pruneStatus: bool = False # For tree pruning application
        self.collapseStatus: bool = False # For tree collapse application
        self.colourStatus: bool = False # For colour labelling application
        self.colourstrainStatus: bool = False # For strain colouring application
        self.heatmapStatus: bool = False # For applying heatmap
        self.heatmapGray: bool = False # For grayscale HM
        self.heatmapBlue: bool = False # For blue/red heatmap (better for value only)
        self.labelstatus: bool = True # For heatmap labels
        self.heatmap_valuestatus: bool = False # To produce a heatmap of values
        self.pruneList: list = [] # List selection for pruning 
        self.collapseList: list = [] #List selection for collapsing

        self.nodefaces: int = 0 # For tree modifications
        self.LTree = None # Processed tree
        self.newick: str = "" # Raw tree file

        self.value = None # For queries

        self.df: str = "" # Initial dataframe
        self.new_df: str = "" # Processed dataframe

        self.hm: str = "" # Initial heatmap
        self.new_hm: str = "" # Processed heatmap
        self.hmcolumns: list = [] # columns
        self.hmrows: list = [] # rows

    # Text output methods for writing concisely to text boxes
    def write(self, content):
        self.insert(tk.END, content)
    def writeln(self, content):
        self.insert(tk.END, content + '\n')

    # Creation of Widgets & autoscroll
    def create_widgets(self):
        """ Create widgets to bulid GUI Interaction. """

        # create instruction label and logo

        # Load the logo image and resize it
        logo_image = Image.open("./img/iff_logo.png")
        logo_image = logo_image.resize((250, 200), Image.LANCZOS)  # Adjust the desired size

        # Convert the resized image to PhotoImage
        logo_image = ImageTk.PhotoImage(logo_image)

        # Create a label to display the logo image
        logo_label = tk.Label(self, image=logo_image)
        logo_label.image = logo_image
        logo_label.grid(row=0, column=0, columnspan=2, rowspan=2, pady=(15, 0))

        # Customize the label appearance
        logo_label.config(bg="#FFFFFF")  # Background color
        logo_label.config(borderwidth=2, relief="solid")  # Add a border
        
        # Creation of buttons
        # Button settings

        # Create a custom style for rounded buttons
        button_style = {"relief": "groove", "background": "#0075CF", "foreground": "#FFFFFF",
                        "font": "Helvetica 12", "width": 20, "anchor": "n"}
        
        #Smaller buttons for two column packing
        button_styleSM = {"relief": "groove", "background": "#0075CF", "foreground": "#FFFFFF",
                        "font": "Helvetica 12", "width": 10, "anchor": "n"}
        
        # Variant small
        
        button_styleSMY = {"relief": "groove", "background": "#EE7600", "foreground": "#FFFFFF",
                        "font": "Helvetica 12", "width": 10, "anchor": "n"}
        
        button_styleRE = {"relief": "groove", "background": "#D31A38", "foreground": "#FFFFFF",
                          "font": "Helvetica 12", "width": 20, "anchor": "n"}
        
        button_styleG = {"relief": "groove", "background": "#03AC13", "foreground": "#FFFFFF",
                         "font": "Helvetica 12", "width": 20, "anchor": "n"}
        
        #Hover styles
        button_styleHover = {"relief": "groove", "background": "#FFFFFF", "foreground": "#000000",
                             "font": "Helvetica 12", "width": 20, "anchor": "n"}
        
        button_styleHoverSM = {"relief": "groove", "background": "#FFFFFF", "foreground": "#000000",
                             "font": "Helvetica 12", "width": 10, "anchor": "n"}
        
        stylevalues = [ttk.Style()] * 5
        style, styleR, styleG, styleSM, styleSMY = stylevalues
        
        style.theme_use('alt')
        styleR.theme_use('alt')
        styleG.theme_use('alt')
        styleSM.theme_use('alt')
        styleSMY.theme_use('alt')

        # Normal Button
        style.configure("NormalButton.TButton", **button_style)
        style.map("NormalButton.TButton")
        # Red Button
        styleR.configure("RedButton.TButton", **button_styleRE)
        styleR.map("RedButton.TButton")
        # Green Button
        styleG.configure("GreenButton.TButton", **button_styleG)
        styleG.map("GreenButton.TButton")
        # Small buttons
        styleSM.configure("SMButton.TButton", **button_styleSM)
        styleSM.map("SMButton.TButton")
        # Small button variant
        styleSMY.configure("SMYButton.TButton", **button_styleSMY)
        styleSMY.map("SMYButton.TButton")


        # Create a custom style for Hover effect
        style.configure('Hover.TButton', **button_styleHover)
        styleSM.configure('HoverSM.TButton', **button_styleHoverSM)

        #Config functions for buttions
        def on_enter(event, button, setting):
            if setting != "Small":
                button.configure(style='Hover.TButton')
            else:
                button.configure(style='HoverSM.TButton')
            
        def on_leave(event, button, setting):
            if setting == "Normal":
                button.configure(style="NormalButton.TButton")
            elif setting == "Red":
                button.configure(style='RedButton.TButton')
            elif setting == "Small":
                button.configure(style='SMButton.TButton')
            elif setting == "SmallY":
                button.configure(style='SMYButton.TButton')
            else:
                button.configure(style='GreenButton.TButton')


        #Button Event Binding
        def bind_hover_events(button, setting):
            if setting == "Normal": 
                button.bind("<Enter>", lambda event: on_enter(event, button, "Normal"))
                button.bind("<Leave>", lambda event: on_leave(event, button, "Normal"))
            elif setting == "Red":
                button.bind("<Enter>", lambda event: on_enter(event, button, "Red"))
                button.bind("<Leave>", lambda event: on_leave(event, button, "Red"))
            elif setting == "Small":
                button.bind("<Enter>", lambda event: on_enter(event, button, "Small"))
                button.bind("<Leave>", lambda event: on_leave(event, button, "Small"))
            elif setting == "SmallY":
                button.bind("<Enter>", lambda event: on_enter(event, button, "Small"))
                button.bind("<Leave>", lambda event: on_leave(event, button, "SmallY"))
            else:
                button.bind("<Enter>", lambda event: on_enter(event, button, "Green"))
                button.bind("<Leave>", lambda event: on_leave(event, button, "Green"))

        # Create buttons and pack them to the parent widget
        button_texts = ["UPLOAD GENOMAP", "UPLOAD TREE FILE", "SHOW TREE ", "RESET", "EXIT", "PRUNE TREE", "COLLAPSE",
                        "CLEAR PRUNE", "LABEL SEARCH", "COL STRAIN", "CLEAR COLOUR", "UPLOAD HM", "ACTIVATE HM", "ABOUT", "EXPORT"]
        
        button_commands = [self.UploadGenogroup, self.UploadTree, self.ShowTree , self.Reset, self.Close, self.treePrune, self.collapseTree,
                           self.clearPrune, self.colourlabel, self.colourStrainActive, self.clearColor, self.UploadHeatmap, self.ApplyHeatmap, self.About,
                           self.export_labelled]
        self.buttons = []
        col=0
        for i, text in enumerate(button_texts):
            if text == "RESET": #Reset and exit buttons with distinct style
                button = ttk.Button(self, text=text, command=button_commands[i], style='RedButton.TButton')
                bind_hover_events(button, "Red")
                button.grid(row=36, column=0, sticky="we", padx=(5,5), columnspan=2)
                self.buttons.append(button)
            elif text == "EXIT":
                button = ttk.Button(self, text=text, command=button_commands[i], style='RedButton.TButton')
                bind_hover_events(button, "Red")
                button.grid(row=38, column=0, padx=(5,5), sticky="we", columnspan=2)
                self.buttons.append(button)
            elif text == "ABOUT":
                button = ttk.Button(self, text=text, command=button_commands[i], style='GreenButton.TButton')
                bind_hover_events(button, "Green")
                button.grid(row=34, column=0, padx=(5,5), sticky="we", columnspan=2)
                self.buttons.append(button)
            elif text == "EXPORT":
                button = ttk.Button(self, text=text, command=button_commands[i], style='NormalButton.TButton')
                bind_hover_events(button, "Normal")
                button.grid(row=32, column=0, padx=(5,5), sticky="we", columnspan=2)
                self.buttons.append(button)
            elif text in button_texts[5:] and text != "ABOUT":
                #Menu associated buttons requiring different placement
                if col == 0 and "HM" in text:
                    button = ttk.Button(self, text=text, command=button_commands[i], style='SMYButton.TButton')
                    bind_hover_events(button, "SmallY")
                    button.grid(row=8+i*2, sticky="we", padx=(5, 3), column=0, columnspan=1)
                    self.buttons.append(button)
                    col=1
                elif col == 1 and "HM" in text:
                    button = ttk.Button(self, text=text, command=button_commands[i], style='SMYButton.TButton')
                    bind_hover_events(button, "SmallY")
                    button.grid(row=8+((i-1)*2), sticky="we", padx=(3, 5), column=1, columnspan=1)
                    self.buttons.append(button)
                    col=0
                elif col == 0:
                    button = ttk.Button(self, text=text, command=button_commands[i], style='SMButton.TButton')
                    bind_hover_events(button, "Small")
                    button.grid(row=8+i*2, sticky="we", padx=(5, 3), column=0, columnspan=1)
                    self.buttons.append(button)
                    col=1
                else:
                    button = ttk.Button(self, text=text, command=button_commands[i], style='SMButton.TButton')
                    bind_hover_events(button, "Small")
                    button.grid(row=8+((i-1)*2), sticky="we", padx=(3, 5), column=1, columnspan=1)
                    self.buttons.append(button)
                    col=0
            else:
                #Beginning buttons positioned with else clause for simplicity
                button = ttk.Button(self, text=text, command=button_commands[i], style='NormalButton.TButton')
                bind_hover_events(button, "Normal")
                button.grid(row=8+i*2, column=0, sticky="we", padx=(5,5), columnspan=2)
                self.buttons.append(button)

        #DROP DOWN MENUS

        # Create a custom style for the menus

        #Menu Events

        #ttk style object

        menu_styleHover = {"relief": "groove", "background": "#FFFFFF", "foreground": "#000000", "font": "Helvetica 12", "width": 28, "anchor": "n"}
        menu_styles = {"relief": "groove", "background": "#0075CF", "foreground": "#FFFFFF", "font": "Helvetica 12", "width": 28, "anchor": "n"}

        Mstyle = ttk.Style()

        # Configure the custom style for the menu buttons
        Mstyle.configure("CustomMenu.TMenubutton", **menu_styles)
        Mstyle.map("CustomMenu.TMenubutton")

        # Configure the custom style for the hover effect
        Mstyle.configure("CustomMenuHover.TMenubutton", **menu_styleHover)
        Mstyle.map("CustomMenuHover.TMenubutton")

        def menu_on_enter(event, menu):
            menu.configure(style="CustomMenuHover.TMenubutton")

        def menu_on_leave(event, menu):
            menu.configure(style="CustomMenu.TMenubutton")

        def bind_menu_events(menu): 
            menu.bind("<Enter>", lambda event: menu_on_enter(event, menu))
            menu.bind("<Leave>", lambda event: menu_on_leave(event, menu))
        
        #Style options for both menus
        
        global options_1, options_2 #Make this globally available to enable update 
        global menu_1, menu_2 #Make this globally available to enable update
        options_1, options_2 = ["LABEL OPTIONS"], ["SELECT STRAINS"]
        global clicked_1, clicked_2 #Make this globally available to enable update 
        clicked_1, clicked_2 = tk.StringVar(), tk.StringVar()
        clicked_1.set("LABEL OPTIONS") #Set name of button
        clicked_2.set("SELECT STRAINS")
        menu_1 = ttk.OptionMenu(self, clicked_1, *options_1) #Genomap label menu
        menu_1.grid(row=14, column=0, sticky="we", padx=(5, 3), columnspan=2)
        menu_1.configure(style="CustomMenu.TMenubutton")
        bind_menu_events(menu_1)
        menu_2 = ttk.OptionMenu(self, clicked_2, *options_2) #Strain subsetting menu
        menu_2.grid(row=16, column=0, sticky="we", padx=(5, 3), columnspan=2)
        menu_2.configure(style="CustomMenu.TMenubutton")
        bind_menu_events(menu_2)

    # Bind the autoscroll() method to the <Button> event of all the buttons
    # Autoscroll bound to text boxes
    def autoscroll(self, event):
        if text_box:
            text_box.see(tk.END)

    # Methods associated with buttons & others
    # Instructions for usage and other details - tied to button
    def About(self):
        """Generates Text Box with Info About Program"""

        #Internal scroll function
        def Aboutscroll_text(*args):
            text_box.yview(*args)

        newWindow = tk.Toplevel(self, bg="lightgrey")
        self.scrollbar = tk.Scrollbar(newWindow, command=Aboutscroll_text)
        self.W1 = tk.Text(newWindow, width=150, height=20)
        self.W1.grid(row=0, column=0, columnspan=5)
        self.W1.configure(font=("Helvetica", 12, "italic"), highlightthickness=1, highlightbackground="black", relief="solid", background="#F0F0F0")
        self.scrollbar.config(command=self.W1.yview)
        self.scrollbar.grid(row=0, column=5, sticky='ns')
        self.W1.config(yscrollcommand=self.scrollbar.set)

        self.W1.tag_configure("bold", font=("Helvetica", 12, "bold", "italic"))

        #Text entered into box
        self.W1.insert(tk.END, "TREE EXPLORER 2023", "bold")
        self.W1.insert(tk.END, "\n\nSoftware package enabling the labelling of phylogenetic trees")
        self.W1.insert(tk.END, "\nusing information derived from genomap tables.")
        self.W1.insert(tk.END, "\n\nUsage:")
        self.W1.insert(tk.END, "\n\nStep 1: Upload genogroup file in csv format ensuring first column contains identifiers")
        self.W1.insert(tk.END, "\nStep 2: Perform label selection BEFORE uploading tree file. Tree labels are modified following upload")
        self.W1.insert(tk.END, "\nStep 3: Upload tree in Newick format.")
        self.W1.insert(tk.END, "\nStep 4: Perform strain selection if you wish to limit tree size otherwise all are shown")
        self.W1.insert(tk.END, "\nStep 5: You can select to crop the tree according to strains selected. Otherwise selections are not taken into account")
        self.W1.insert(tk.END, "\n\tIn addition you can collapse branches containing selected strains instead of cropping so you have a simpler tree")
        self.W1.insert(tk.END, "\n\tbut with the possibility to open the branches as you wish.")
        self.W1.insert(tk.END, "\nStep 6: Click 'Show Tree' to display and explore the result")
        self.W1.insert(tk.END, "\n\nClick 'Reset' to start a new analysis and 'Exit' to quit the program")

        self.W1.insert(tk.END, "\n\nColour Leaf Queries", "bold")
        self.W1.insert(tk.END, "\n\nA basic tool has been added which allows the user to search for specific characteristics and colour those accordingly.")
        self.W1.insert(tk.END, "\nIn order to do this, you must enter queries in a specific form as follows: LABEL=1 AND LABEL=2 AND COLOUR=X")
        self.W1.insert(tk.END, "\nfor example to highlight strains in yellow that are prtS positive (with 1/0 notation) you enter: prts_1 AND yellow.")
        self.W1.insert(tk.END, "\nThe label entered reflects the structure of the genomap file so change this accordingly.")
        self.W1.insert(tk.END, "\n\nMultiple queries can also be performed along with more complex requests such as searching for ranges.")
        self.W1.insert(tk.END, "\nSearches are separated with the 'AND' keyword. The following notation allows you to perform searches for")
        self.W1.insert(tk.END, "\nspecific values:")
        self.W1.insert(tk.END, "\n\npH=(G,5) search for pH greater than 5")
        self.W1.insert(tk.END, "\npH=(L,5) search for pH less than 5")
        self.W1.insert(tk.END, "\npH=(4,5) search for pH between 4 and 5")

        self.W1.insert(tk.END, "\n\nAll these queries can be combined for example: ")
        self.W1.insert(tk.END, "\nprtS=1 AND pH=(L,5) AND Lysotype=SoS-ST0234-SX AND DoublingTime=(20,25) AND colour=yellow")
        self.W1.insert(tk.END, "\nWill find prtS positive strains with pH less than 5, the lysotype of ST0234 and a doubling time between 20 and 25 minutes.")
        self.W1.insert(tk.END, "\n\nThis functionality is quite sensitive so whilst you will be informed of some mistakes")
        self.W1.insert(tk.END, "\nit is possible that in some cases the absence of highlighting is due to an unusual error. So be careful.")

        self.W1.insert(tk.END, "\nWhen the tree is displayed strains matching the search criteria will be coloured.")
        self.W1.insert(tk.END, "\nThis function is at an early stage and can be expanded depending on user feedback.")

        self.W1.insert(tk.END, "\n\nAdding Custom Labels", "bold")
        self.W1.insert(tk.END, "\n\nYou are not limited to using preset options in the genomap file. You are free to add as many as you want.")
        self.W1.insert(tk.END, "\nSimply open the genomap file and add the column header and relevant values that you want.")
        self.W1.insert(tk.END, "\nThere is no limit though if possible avoid unusual characters or symbols in label headers and values.")

        self.W1.insert(tk.END, "\n\nHeatmaps", "bold")
        self.W1.insert(tk.END, "\n\nAn additional functionality allows for the addition of heatmaps to phylogenetic trees.")
        self.W1.insert(tk.END, "\nTo use this you need to upload a file with the genome identifiers and the various information you wish to display")
        self.W1.insert(tk.END, "\nThis can be presence/absence info of type +/- for example when dealing with genes.")
        self.W1.insert(tk.END, "\nYou may also upload raw numeric data which will be displayed accordingly. E.g. raw measures.")
        self.W1.insert(tk.END, "\nAfter upload click to apply the heatmap and select the desired formatting options (e.g. grayscale or remove column names etc)")

        self.W1.insert(tk.END, "\n\nExplanations for Each Button", "bold")
        self.W1.insert(tk.END, "\n\nUpload Genomap: To upload your table containing strain names and characteristics of interest.")
        self.W1.insert(tk.END, "\nUpload Tree File: To upload your phylogenetic tree in newick format.")
        self.W1.insert(tk.END, "\nShow Tree: Display tree.")
        self.W1.insert(tk.END, "\nReset: Remove all files and formatting to start a new analysis.")
        self.W1.insert(tk.END, "\nExit: Close the program.")
        self.W1.insert(tk.END, "\nPrune Tree: Remove branches for all EXCEPT selected strains.")
        self.W1.insert(tk.END, "\nCollapse: close branches containing selected strains. These can be expanded.")
        self.W1.insert(tk.END, "\nClear Prune: Remove both pruning and collapse options.")
        self.W1.insert(tk.END, "\nLabel Search: perform search of tree to colour branches of interest.")
        self.W1.insert(tk.END, "\nCol Strain: Colour selected strains.")
        self.W1.insert(tk.END, "\nClear Colour: Remove all colour formatting.")
        self.W1.insert(tk.END, "\nAbout: Opens this box.")
        self.W1.insert(tk.END, "\nLabel Options: Contains characteristics derived from genomap file.")
        self.W1.insert(tk.END, "\nSelect Strains: Select strains for further analysis.")
        self.W1.insert(tk.END, "\nExport: Output labelled data to csv file for colour coded strains.")
        self.W1.insert(tk.END, "\nUpload HM: Upload you heatmap file if desired.")
        self.W1.insert(tk.END, "\nActivate HM: apply formatting and show heatmap.")
        

        self.W1.insert(tk.END, "\n\nTroubleshooting", "bold")
        self.W1.insert(tk.END, "\n\nWill be filled with resolutions as users report challenges in using program")

        self.W1.insert(tk.END, "\n\nIf you are generally pleased with this software but have some things you would like")
        self.W1.insert(tk.END, "\nto see included or changed, do not hesitate to get in contact!")
        self.W1.insert(tk.END, "\n\nSupport/Requests/Questions: damian.magill@iff.com", "bold")

    # Closes program 
    def Close(self):
        """Closes the Program"""
        root.destroy()
        sys.exit()

    # Upload and processing of genogroup file - menus also updated
    def UploadGenogroup(self):
        """Genogroup File Upload"""
        text_box.delete(1.0,tk.END)
        filename = filedialog.askopenfilename()
        if filename:
            if "csv" or "xls" in filename:
                text_box.insert(tk.END, '\n\nSelected: ' + str(filename))
                #Data processing
                if "csv" in filename:
                    self.df = pd.read_csv(filename, encoding="ISO-8859-1")
                else:
                    self.df = pd.read_excel(filename)
                #Remove characters that may cause problems
                self.df = self.df.apply(lambda x: x.replace('(','').replace(')',''))
                #Modify Data to include header
                colnames = self.df.columns.values.tolist() #Extract column names
                colnames.pop(0) #Do not include genome name as this is needed to reference tree

                self.UpdateMenuGeno(menu_1, clicked_1, self.df)
                self.UpdateMenuStrain(menu_2, clicked_2, self.df)
            else:
                self.call_error(8) # File invalid error

            #Modification of DF values to provide meaningful labels for the tree (e.g. Prts-1 instead of simply 1)
            for i in colnames:
                self.df[i] = str(i).replace('(','').replace(')','') + "_" + self.df[i].astype(str).replace("nan", "NONE") 
            text_box.insert(tk.END, '\n\nPlease apply subsetting before tree upload if desired.')
        else:
            text_box.insert(tk.END, "Please upload a genomap and/or tree file to get started.")
    
    # Upload of tree file
    def UploadTree(self):
        """Newick file upload"""
        def newick_QC(filename):
            """Quick QC on newick file"""
            extensions = ["nw", "nwk", "newick", "nk"]
            if not any(i.upper() for i in extensions if i in filename.upper()):
                return False
            return True

        if not isinstance(self.df, str):
            if not self.subList:
                answer = askyesno(title='Genotype Subsetting',
                message='Are you happy to build a tree with no labels?')
                if answer:
                    self.subset(self.df, self.subList)
                    text_box.delete(1.0,tk.END)
                    filename = filedialog.askopenfilename()
                    if not newick_QC(str(filename)):
                        self.call_error(5)
                    try:
                        text_box.insert(tk.END, '\n\nSelected: ' + str(filename))
                        with open(filename, "r") as f:
                                self.newick = f.read()
                        return self.newickModify(self.newick, self.newdf)
                    except IOError:
                        self.call_error(5)
                else:
                    text_box.insert(tk.END, '\n\nPlease subset genogroups before uploading tree file')
            else:
                self.subset(self.df, self.subList)
                text_box.delete(1.0,tk.END)
                filename = filedialog.askopenfilename()
                text_box.insert(tk.END, '\n\nSelected: ' + str(filename))
                with open(filename, "r") as f:
                    self.newick = f.read()
                return self.newickModify(self.newick, self.newdf)
        else:
            answer = askyesno(title='Only Tree Upload',
                message='You are uploading a tree without genomap file. Do you wish to proceed?')
            if answer:
                text_box.delete(1.0,tk.END)
                filename = filedialog.askopenfilename()
                text_box.insert(tk.END, '\n\nSelected: ' + str(filename))
                with open(filename, "r") as f:
                    self.newick = f.read()
                self.LTree = Tree(self.newick)
                return self.LTree
            else:
                text_box.insert(tk.END, '\n\nPlease Upload Genomap and/or tree files.')

    # Heatmap formatting options
    def heatmap_options(self):
        """Provides options for heatmap formatting"""
        # Nested functions

        # Determine status for heatmap colours
        def heatmap_colour(col):
            """select colour palette"""
            text_box.insert(tk.END, f'\n\nSelected option: {col}')
            self.heatmapGray = col == "Grayscale" # Make true (change if other colours added in future)
            self.heatmapBlue = col == "Blue-Red"
            selected.set(col)
            update_button_styles()
            
        # Labels for each heatmap column
        def heatmap_label(status):
            """Status change for whether labels required or not"""
            self.labelstatus = status
            text_box.insert(tk.END, '\n\nLabels Applied!') if status else text_box.insert(tk.END, '\n\nLabels Not Applied!')
            selected.set("Labels") if status else selected.set("No Labels")
            update_button_styles()      

        # Display values instead of blocks
        def heatmap_value(status):
            """Status change for value only heatmap"""
            self.heatmap_valuestatus = status
            text_box.insert(tk.END, '\n\nValue only heatmap selected') if status else text_box.insert(tk.END, '\n\nRegular heatmap selected')
            selected.set("Value Only Heatmap") if status else selected.set("Regular Heatmap")
            update_button_styles() 

            # Update button styles based on the selected option
        
        def update_button_styles():
            for button in buttons:
                button.configure(**button_styles["normal"])  # Reset all buttons to normal style

            selected_option = selected.get()
            for button in buttons:
                if button["text"] == selected_option:
                    button.configure(**button_styles["selected"])  # Apply selected style to the selected button
                    break
        
        #Close menu
        def close():
            """Remove option menu"""
            radioWindow.destroy()

        # top level window
        radioWindow = tk.Toplevel(self, bg="#0075CF")

        # Options with associated functions
        options = [
            ("Colour Scheme", [
                ("Grayscale", lambda: heatmap_colour("Grayscale")),
                ("Red-Orange-Yellow", lambda: heatmap_colour("Red-Orange-Yellow")),
                ("Blue-Red", lambda: heatmap_colour("Blue-Red"))
            ]),
            ("Heatmap Labels", [
                ("Labels", lambda: heatmap_label(True)),
                ("No Labels", lambda: heatmap_label(False))
            ]),
            ("Heatmap Type", [
                ("Value Only Heatmap", lambda: heatmap_value(True)),
                ("Regular Heatmap", lambda: heatmap_value(False))
            ]),
            ("Close", [
                ("Close", lambda: close())
            ])
                ]

        # Create a variable to store the selected option
        selected = tk.StringVar()

        # Define button styles
        button_styles = {
            "normal": {"relief": tk.RAISED, "width": 20},
            "selected": {"relief": tk.SUNKEN, "width": 20, "bg": "#D31A38", "fg": "#FFFFFF"}
        }

        buttons = []  # Store the buttons in a list for easier access

        for title, button_options in options:
            title_label = tk.Label(radioWindow, text=title, font=("Arial", 12, "bold"), anchor="w", fg="#FFFFFF", bg="#0075CF")
            title_label.pack(pady=5)

            for text, command in button_options:
                button = tk.Button(radioWindow, text=text, command=command, **button_styles["normal"])
                button.pack(pady=5)
                buttons.append(button)  # Add the button to the list

        update_button_styles()  # Set initial button styles based on the selected option

        # Need to return to allow menu to wait and then execute future code block
        return radioWindow

    # Upload of heatmap if desired
    def UploadHeatmap(self):
        """Upload heatmap file for display on tree"""
        text_box.delete(1.0,tk.END)
        #MAKE WARNING APPEAR - No labels on tree
        answer = askyesno(title='Heatmap Construction',
                message='Heatmaps may not work alongside genomap labels. Are you happy to continue?')
        if answer:
            heatmap = filedialog.askopenfilename()
            if heatmap:
                if "csv" or "xls" in heatmap:
                    text_box.insert(tk.END, '\n\nSelected: ' + str(heatmap))
                    #Data processing
                    if "csv" in heatmap:
                        self.hm = pd.read_csv(heatmap, encoding="ISO-8859-1")
                    else:
                        self.hm = pd.read_excel(heatmap)

                self.new_hm = self.minmaxdf(self.hm) # Process dataframe to heatmap
                # Convert heatmap to dictionary
                text_box.insert(tk.END, "\n\nHeatmap successfully processed!")
            else:
                self.call_error(8) # File invalid error
        else:
            text_box.insert(tk.END, "\n\nPlease upload heatmap on a label free map to continue.")

    # Normalize dataframe and deal with other data types plus process
    def minmaxdf(self, df):
        """Normalize values in df and perform other processing"""

        # Need some internal functions

        # Displays output when exception raised

        # Check for missing values
        def is_NaN(val):
            """Check if value is NAN"""
            return val != val

        # Iteration over DF for quality checking
        def col_iter(df):
            """Allows iteration over whole dataframe"""
            cols = df.columns.values.tolist()
            for _, i in df.iterrows():
                for j in cols:
                    if is_NaN(i[j]):    # Apply is_NaN and raise error if true - message displayed
                        raise ValueError(self.call_error(1)) # Error function called
                    
        # First column is index
        df = df.set_index(df.columns[0])
        col_iter(df) # Blank value check
        
        # OTHER VALUES TO REPLACE

        value_replacement = {"+": 1, "-": 0, "Y": 1, "N": 0} # Values replaced in df for presence/absence
        for k in value_replacement:
            if df.isin([k]).any().any():
                df.replace(k, value_replacement[k], inplace=True) 
        
        # Min/Max scaling with handling for edge cases
        df_min = df.min()
        df_max = df.max()
        df_range = df_max - df_min # Value difference
        df_range_nonzero = df_range.replace(0, 1)  # Replace zero range with 1 to avoid zero div errors
        df_scaled = (df - df_min) / df_range_nonzero
        
        # Handle case when all values are 1 to avoid NaN being generated
        if (df_scaled == 1).all().all():
            df_scaled = df_scaled.replace(1, 0)
        
        self.hmcolumns = df_scaled.columns.values.tolist()
        
        heatmap_data = []
        for index, row in df_scaled.iterrows():
            values = row.tolist()
            name = index
            data = {"name": name, "values": values}
            heatmap_data.append(data)

        return heatmap_data

    # Performs update of genogroup menu providing select options and click traces
    def UpdateMenuGeno(self, menu, var, df):
        """Update Menu Options Based on Uploads"""
        menu.configure(state='normal') # Enable drop down
        menu = menu['menu']
        menu.delete(0, 'end')
        for col in df.columns.values.tolist()[1:]:
            # Add menu items
            menu.add_command(label=col, command=lambda col=col: var.set(col))
        var.trace("w", self.GenogroupSelector)
        return menu
        
    # Performs update of strain menu providing select options and click traces
    def UpdateMenuStrain(self, menu, var, df):
        """Update Strain Menu Options Based on Uploads"""
        menu.configure(state='normal') # Enable drop down
        menu = menu['menu']
        menu.delete(0, 'end')
        for i, r in df.iterrows():
            # Add menu items
            try:
                if "GenomeID" in df.columns:
                    x = r["GenomeID"]
                else:
                    x = r.iloc[0]
            except IOError:
                self.call_error(9) # call error on genome ID
            menu.add_command(label=x, command=lambda x=x: var.set(x))
        var.trace("w", self.StrainSelector)
        return menu

    # Updates list with genogroup selections for later subsetting
    def GenogroupSelector(self, *args):
        """Retrieve items selected from genogroup menu"""
        temp = str(clicked_1.get())
        if temp not in self.subList:
            self.subList.append(temp)
            text_box.delete(1.0,tk.END)
            text_box.insert(tk.END, '\nSelected: ' + ", ".join(self.subList))
        else:
            text_box.insert(tk.END, '\n' + temp + ' already selected!') 

    # Updates list with strain selections for ltree collapse
    def StrainSelector(self, *args):
        """Retrieve strains selected from strains menu"""
        temp = str(clicked_2.get())
        if temp not in self.strainList:
            self.strainList.append(temp)
            text_box.delete(1.0,tk.END)
            text_box.insert(tk.END, '\nSelected: ' + ", ".join(self.strainList))
        else:
            text_box.insert(tk.END, '\n' + temp + ' already selected!') 

    # Subset genogroups method
    def subset(self, df, subList): # ADJUST WITH SELECTED VALUES
        """Function applying subset values to return new DF"""
        # add function to read in sublist
        id = df.columns.values.tolist()[0]
        subList.insert(0, id)
        self.newdf = df.filter(subList, axis=1)
        # create new row which will be tree label
        self.newdf['Label'] = self.newdf[[col for col in self.newdf.columns]].agg(' // '.join, axis=1)
        return self.newdf

    # Modify Newick tree labels according to genogroup selections & return tree object
    def newickModify(self, tree, newdf):
        IDList, Labels = [],[]
        if "GenomeID" not in newdf.columns:
            text_box.insert(tk.END, "\n\nGenomeID column not detected. Attempting extraction nonetheless...")
        for i, j in newdf.iterrows():
            try:
                if "GenomeID" in newdf.columns:
                    IDList.append(j["GenomeID"]) # extract genome ID
                else:
                    IDList.append(j.iloc[0]) # extract first column if genome ID not present
            except IOError:
                self.call_error(9) # call error for genome ID problems
            Labels.append(j["Label"])
        for idx, item in enumerate(IDList):
            self.reference.update({str(item):str(Labels[idx])})
            tree = tree.replace(str(item), str(Labels[idx]))
        self.LTree = Tree(tree)
        return self.LTree

    # Prune tree based on selected strains
    def treePrune(self):
        """Generate a sublist used for pruning the tree later"""
        if self.strainList:
            for item in self.strainList:
                self.pruneList.append(self.reference[item]) #using strain values get labels created
                self.pruneStatus = True
        else:
            text_box.insert(tk.END, "\nCannot prune tree as no strains have been selected!")
        return self.pruneList

    # Remove both pruning and collapse options
    def clearPrune(self):
        """Clears strain subset list to reverse pruning effects"""
        try:
            self.pruneList, self.collapseList, self.strainList = [],[],[]
            self.pruneStatus, self.collapseStatus = False, False
            self.nodefaces = 0
 
            for leaf in self.LTree.get_leaves():
                self.LTree.img_style["draw_descendants"] = True

            self.newickModify(self.newick, self.newdf)

            text_box.insert(tk.END, "\n\nPruning and/or collapse options have been cleared!")
            text_box.insert(tk.END, "\nYou may now display the entire tree or apply new parameters")
        except AttributeError:
            text_box.insert(tk.END, "\nNothing to clear!")

    # Open custom menu box - needed for queries
    def open_custom_dialog(self):
        """Custom dialog box for queries"""
        self.dialog = tk.Toplevel(root)
        self.dialog.geometry("500x250")
        label = tk.Label(self.dialog, text="Enter your search query:")
        label.pack()
        self.entry = tk.Entry(self.dialog, width=75)
        self.entry.pack()
        submit_button = tk.Button(self.dialog, text="Submit", command=self.submit_input)
        submit_button.pack()

    # Get queries input from dialogue box
    def submit_input(self):
        """Get input from query and pass to function"""
        self.value = self.entry.get()
        text_box.insert(tk.END, f'\n\nYou entered: \"{self.value}\"')
        self.dialog.destroy()
        self.process_value()

    # Check that queries conform to what is expected and provide approriate warnings
    def qualitycheck(self, input):
        """Performs series of quality checks on query inputs"""
        COMMONCOLOURS = ["RED", "YELLOW", "GREEN", "BLUE", "BLACK", "ORANGE", "PINK", "BROWN", "GRAY", "#"]
        if "AND" not in input.upper():
            self.call_error(2)
        if not any(i for i in COMMONCOLOURS if i in input.upper()):
            self.call_error(3)
        if "=" not in input.upper():
            self.call_error(4)

    # Process query values
    def process_value(self):
        """Process query"""
        if self.value:
            #Perform some quality checks
            self.qualitycheck(self.value)
            #Process input
            self.value = self.value.replace("=", "_").replace("and", "AND") # to also accept = nomenclature
            self.value = self.value.split(sep=" AND ")
            if len(self.value) == 1:
                self.value.append("#FEE715")
            self.colourStatus = True
            return self.value
        else:
            text_box.insert(tk.END, "\nPlease enter label names and colour if you wish to add colour coding to the tree.")

    # Tied to button to open dialg box
    def colourlabel(self):
        """Dialog box for queries"""
        self.value = None # Reset to allow new queries
        self.open_custom_dialog()
    
    # Method to deal with range queries
    def evaluateRange(self, NameValue, condition):
        """function to evaluate node names meeting range condition"""
        ACCEPTED_LESS = ("L", "LESS", "LESS THAN", "LT", "LOWER", "BELOW", "LESSTHAN", "UNDER")
        ACCEPTED_MORE = ("G", "GREATER", "GREATER THAN", "GT", "HIGHER", "MORE", "ABOVE", "GREATERTHAN")
        if isinstance(condition, str):
            testcondition = condition.split("_")[-1].replace("(","").replace(")","").split(",") # Pull entered values for testing and split to obtain needed value
        else:
            testcondition = condition[-1].replace("(","").replace(")","").split(",")
        if len(testcondition) != 2: # Skip entries that are not valid conditions
            pass
        else:
            try:
                float(NameValue[1])
                float(testcondition[1]) # test that value in question is testable to avoid errors  
                if testcondition[0].upper() in ACCEPTED_LESS: # if request is to search values less than that specified
                    if float(NameValue[1]) < float(testcondition[1]):
                        return True
                    return False
                elif testcondition[0].upper() in ACCEPTED_MORE: # if request is to search values greater than that specified
                    if float(NameValue[1]) >= float(testcondition[1]):
                        return True
                    return False       
                elif float(NameValue[1]) >= float(testcondition[0]) and float(NameValue[1]) <= float(testcondition[1]): # select a range of values
                        return True
                else:
                    return False # catch other cases
            except (ValueError, TypeError, IndexError):
                print("Data type Error!")      

    # Methods passed here to conduct actual leaf colouring
    def colorLeaves(self, node, value):
    # Define the condition to determine leaf colors
        colourvals = ("COLOUR", "COLOR", "COL")
        if not any("(" in i for i in value[0:len(value)-1]): # this block runs if no complex queries are written. This limits possibility of errors.
            if all(i.upper() in node.name.upper() for i in value[0:len(value)-1]):
                if any(i for i in colourvals if i in value[-1].upper()):
                    temp = value[-1].split("_")[1]
                    node.img_style["bgcolor"] = temp
                else:
                    node.img_style["bgcolor"] = value[-1]
            else:
                node.img_style["bgcolor"] = "white"
        #Add logic to deal with ranges 
        else:
            valuetest = [i.split("_") for i in value[0:len(value)-1]]
            nodetest = [x.split("_") for x in node.name.upper().split(" // ")[1:]] # create list of lists dividing each label with its corresponding value
            valid = [False for i in range(0, len(value)-1)] #need to validate all search criteria in order to colour branch
            for i, item in enumerate(valuetest):
                for j in nodetest:
                    if item[0].upper() == j[0].upper() and "(" not in item[1]: # Evaluate non-complex values as direct comparisons
                        if item[1].upper() == j[1].upper():
                            valid[i] = True
                    elif item[0].upper() == j[0].upper() and "(" in item[1]: # Evaluate complex expressions with range function
                        if self.evaluateRange(j, item):
                            valid[i] = True
            if all(valid): #Colour only if all requested conditions are met
                if any(i for i in colourvals if i in value[-1].upper()):
                    temp = value[-1].split("_")[1]
                    node.img_style["bgcolor"] = temp
                else:
                    node.img_style["bgcolor"] = value[-1]
            else:
                node.img_style["bgcolor"] = "white"

    # Remove all colour formatting
    def clearColor(self):
        """Remove colour labels from tree"""
        self.colourstrainStatus, self.colourStatus = False, False
        self.value = None
        for i in self.LTree.get_leaves():
            i.img_style['bgcolor'] = "#FFFFFF"
        text_box.insert(tk.END, "\nColour labelling has been cleared!.")

    # Use dictionary to reference original names and change tree acordingly
    # Fix tree upload first

    # Collapse strains not selected
    def collapseTree(self):
        """Collapse nodes not selected in sublist"""
        if not self.pruneStatus:
            for item in self.strainList:
                self.collapseList.append(self.reference[item])
            self.collapseStatus = True
            return self.collapseList
        else:
            text_box.insert(tk.END, 'Pruning options have already been applied. Please reset options to collapse.')

    # Collapse branches containing selected strains
    def collapseBranches(self, node, depth):
        if depth == 0:
            for leaf in node.get_leaves():
                if leaf.name in self.collapseList:
                    node.img_style["draw_descendants"] = False
                    return
        elif not node.is_leaf():
            for child in node.children:
                self.collapseBranches(child, depth - 1) #Change depth to modify collapse extent

    # Method 1 to colour strains in subset list
    def colourStrainActive(self):
        self.colourstrainStatus = True
    
    # Method 2 to colour strains in subset list
    def colourStrain(self, node):
        for i in self.strainList:
            if i in node.name:
                node.img_style["bgcolor"] = "#FEE715"

    # Export labelled information to external file
    def export_labelled(self):
        """Method allowing CSV export of tree names that have been color labelled"""
        try:
            if self.LTree:  # Check that tree exists
                output_list = []
                for node in self.LTree.iter_descendants():  # Traverse all nodes in tree
                    if "bgcolor" in node.img_style and node.img_style["bgcolor"] != "#FFFFFF":
                        if node.is_leaf():  # Only consider labeled leaves 
                            output_list.append(node.name)
                        else:
                            # Traverse descendants to include labeled leaves in subtrees
                            labeled_leaves = [leaf.name for leaf in node.iter_leaves() if
                                            "bgcolor" in leaf.img_style and leaf.img_style["bgcolor"] != "#FFFFFF"]
                            print(labeled_leaves)
                            output_list.extend(labeled_leaves)
                if not output_list:
                    text_box.insert(tk.END, "\nNothing labeled to export!")
                else:
                    filename = simpledialog.askstring("Output Filename", "Enter output file name: ")
                    if ".csv" not in filename:
                        filename = f"{filename}.csv"
                    with open(filename, "w") as f: # Output to csv
                        for name in output_list:
                            f.write(f"{name.replace(' // ', ',')}\n")
                    text_box.insert(tk.END, "\nExport successful!")
            else:
                text_box.insert(tk.END, "\nNo tree generated to perform the selected action!")
        except AttributeError: # Capture error when no tree created 
            text_box.insert(tk.END, "\nError occurred during export process! Have you created a tree?")

    # Generate colours for heatmap
    def generate_color(self, value, code):
        if code == 1:
            # Convert values between 0 and 1 to 255 scale
            gray_value = int((1 - value) * 255)
            # Derive hex code for grayscale from this value
            hex_code = "#{:02X}{:02X}{:02X}".format(gray_value, gray_value, gray_value)
        elif code == 2:
            # Calculate the green component based on the value
            red = int((value) * 255)
            blue = int((1-value) * 255) 
            # Generate the hex code for the color (white to green gradient)
            hex_code = "#{:02X}{:02X}{:02X}".format(red, 0, blue)
        else:
            # Calculate the green component based on the value
            green = int((1 - value) * 255)
            # Generate the hex code for the color (white to green gradient)
            hex_code = "#{:02X}{:02X}{:02X}".format(255, green, 0)

        return hex_code

    # Add heatmap with selected formatting to tree
    def ApplyHeatmap(self):
        # Display the menu at the location of the button
        if not isinstance(self.new_hm, str):
            if self.LTree:
                heatmap_window = self.heatmap_options()
                self.wait_window(heatmap_window)
                self.heatmapStatus = not self.heatmapStatus
                text_box.insert(tk.END, "\n\nHeatmap has been applied. You may now display the tree.")
            else:
                self.call_error(6)
        else:
            self.call_error(7)
    
    # Apply tree settings and show
    def ShowTree(self):
        # Style the tree with basic features
        ts = TreeStyle()
        ts.show_leaf_name = False
        ts.branch_vertical_margin = 10
        ts.scale = 120
        # Apply styles and Show Tree
        if self.LTree:
            for node in self.LTree.traverse():
                # disable default node shapes
                node.img_style["size"] = 10
                node.img_style["shape"] = "sphere"
                node.img_style["fgcolor"] = "darkred"
                # Add tip names in a custom position
                if node.is_leaf() and self.nodefaces == 0:
                    nameF = AttrFace("name", fsize=10, fgcolor="slateGrey")
                    node.add_face(nameF, column=1, position="branch-right")

            self.nodefaces += 1 #Stops duplication of names 
            # Pruning if requested
            if self.pruneStatus:
                self.LTree.prune(self.pruneList)
            
            # Collapse nodes not containing selected strains
            if self.collapseStatus:
                self.collapseBranches(self.LTree, 2) 

            # Colour tree leaves if requested

            if self.colourStatus:
                for leaf in self.LTree.iter_leaves():
                    self.colorLeaves(leaf, self.value)
            
            # Apply strain colouring if selected

            if self.colourstrainStatus:
                for leaf in self.LTree.iter_leaves():
                    self.colourStrain(leaf)

            # Building the heatmap
            if self.heatmapStatus:
                # Create rectangular faces in order to build heatmap

                num_columns = len(self.new_hm[0]["values"]) # Get the number of columns
                for column in range(num_columns):
                    for data in self.new_hm:
                        leaf_name = data["name"]
                        values = data["values"]
                        value = values[column]
                        leaf_node = self.LTree & leaf_name # Get the node corresponding to the leaf name
                        if self.heatmapGray:
                            color = self.generate_color(value, 1) # Customize colors based on presence/absence
                        elif self.heatmapBlue:
                            color = self.generate_color(value, 2) # Customize colors based on presence/absence
                        else:
                            color = self.generate_color(value, 3) # Customize colors based on presence/absence

                        if self.heatmap_valuestatus:
                            value_face = TextFace(text=f'{value:.2f}_', fsize=5, fgcolor=color, bold=True) # limit values to 2 SF otherwise display is crowded
                            leaf_node.add_face(value_face, column=column, position="aligned")
                        else:
                            rect_face = RectFace(width=30, height=30, fgcolor="black", bgcolor=color, label="X")
                            leaf_node.add_face(rect_face, column=column, position="aligned")
                    
                # Add label for each column as a header if desired (this is the default)
                    if self.labelstatus:
                        column_label = TextFace(f"{self.hmcolumns[column]}", fsize=10) # Retrieve col name by index
                        column_label.rotation = 90 # Rotate the label by 90 degrees
                        ts.aligned_header.add_face(column_label, column=column)      

            # Show the tree
            self.master.attributes("-disabled", True) # Freeze the main window when tree is displayed
            self.LTree.show(tree_style=ts)
            self.master.attributes("-disabled", False) # Unfreeze the main window when tree is displayed
            self.master.deiconify() # Keep tkinter window in front
        else:
            text_box.insert(tk.END, '\n\nNo valid tree can be created. Have you uploaded all files?')
  
    # Clears all inputs for new analysis
    def Reset(self):
        """Function to Wipe all Settings"""
        self.subList, self.pruneList, self.strainList, self.collapseList = [],[],[],[]
        self.reference = {} #Dictionary allowing modified newick filename retrieval from original strain name (GenomeID)
        val = [False] * 7
        self.pruneStatus, self.collapseStatus, self.colourStatus, self.colourstrainStatus, self.heatmap_valuestatus, self.heatmapStatus, self.heatmapGray = val
        self.labelstatus = True
        self.nodefaces = 0 #Counter to limit duplicate branch names when tree reloaded
        self.df, self.newdf, self.LTree = "", "", None
        self.options_1, self.options_2 = ["NONE"],["NONE"]
        self.new_hm, self.hm = "", ""
        self.create_widgets() # Recreate menu buttons
        text_box.delete(1.0,tk.END)
        text_box.insert(tk.END, 'Console Reset. Please upload new files.')

    # Blank function used when creating new buttons
    def temp(self):
        text_box.insert(tk.END, "\nButton reserved for future functionality.")

    # Grouping error messages
    def call_error(self, code):
        reference = {
            1:"WARNING! You may have missing data in your table.\nYou cannot proceed without fixing your data.\nPleasecheck your file.\nIf issues persists despite no apparent problem. Please get in contact.",
            2:"Warning! Conjunction missing from query or mistake present.\nThis does not mean your query will not run so please try first",
            3:"Note! Did you specify a colour? If yes please ignore this message!\nThis does not mean your query will not run so please try first",
            4:"Warning! You may be missing a character from one or more of your labels.\nThis does not necessarily mean your query will not run so please try first.",
            5:"Something went wrong. Please check that your file is in Newick format.",
            6:"No tree uploaded! Cannot perform function!",
            7:"No heatmap uploaded! Cannot perform function!",
            8:"File not valid. Please upload file in Excel or csv format. If problems persist get in touch.",
            9:"Issue with GenomeID Extraction. Ensure that IDs matching tree branch names are in the first column of the table. You can extract these from your tree using the other tools section"
        }
        text_box.insert(tk.END, f'\n\n{reference[code]}')

    # Window Freezing functions - to bypass GIL release bug
    # Freeze the main window
    def freeze_window(self):
        root.grab_set()
    # Unfreeze the main window
    def unfreeze_window(self):
        root.grab_release()

# Main Portion of Program

def main():
    # Main Functions
    def scroll_text(*args):
        text_box.yview(*args)
    # Other
    global root
    root = tk.Tk()
    root.title("Tree Explorer")
    root.configure(background="lightgrey")
    app = Application(root)
    app.configure(bg="lightgrey")

    # Building text box
    global text_box
    scrollbar = tk.Scrollbar(app, command=scroll_text) # Adding Y-axis scrollbar and configuring
    text_box = tk.Text(app, width = 130, height = 32, yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_box.yview)
    text_box.grid(row = 0, column = 4, columnspan = 4, rowspan=40, pady=(15,10))
    text_box.configure(font=("Helvetica", 12, "italic"), highlightthickness=1, highlightbackground="black", relief="solid", background="#F0F0F0")
    scrollbar.grid(row=0, column=10, sticky='ns')
    text_box.insert(tk.END, "Welcome to Tree Explorer.\n\nPlease upload genogroup and tree files to get started. \n\nClick 'About' for more information.")

    root.mainloop()

if __name__ == '__main__':
    main()