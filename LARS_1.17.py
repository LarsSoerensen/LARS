# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 14:02:59 2014

@author: Lars Sørensen
"""

#=======================================================================================
# Several globally defined values are used through out the program they are listed here:
#   RT
#   pre_selection_list
#   filelocation_list
#   key_list
#   Dialog
#   Prot_ident        
#   MinInt
#   ScrMinInt        
#   MinSeqLen       
#   MaxSeqLen        
#   MinProd
#   ScrMinProd      
#   MinProdPAA
#   ScrMinProdPAA        
#   MinConProd
#   ScrMinConProd        
#   MinScr
#   ScrMinScr        
#   MaxMHHErr        
#   NoOffRep        
#   ScrNoOffRep       
#   Allowed_SD
#   Sequence_Length
#   MinSeqScr
#   Show caution when using these
#=======================================================================================

#The necessary modules are importede
import sys
import csv 
import re
import os
import datetime
import ntpath
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import StringVar
from tkinter import ttk
from tkinter import Event
from tkinter import messagebox

class ToolTip(object):
    """
    This class is a modified version of the one found here http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
    it allows for the attachement of tool tip to entryboxes, labels and all other widgets from tkinter
    """

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify="left",
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        """
        Removes the tool tip. called upon exiting the widgets
        """
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text): 
    """
    Creates the tooltip from the tooltip class, and displays the text given to the function when the cursor enters 
    or exit the widget 
    """
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class RT_Selection_Treeview(object):
    """
    When an RT SD fails to meet the users input this class is called
    The class contains the window settings, a function that builds the treeview and a function that allows 
    the user to select the RT that they want
    """
    def __init__(self,root):
        """
        The __init__ builds the window and the treeview widget 
        """
        # The settings for the geometry of the window and column names
        self.top = tk.Toplevel()
        self.top.geometry("800x300")
        self.top.focus()
        self.label=tk.Label(self.top,text="Select your RT")
        self.label.pack()
        self.columns = ["Sequence", "No. Products", "Intensity", "RT", "IM", " z ",  "Delta mass"]#The items in this list are used for column headers
        self.tree = tk.ttk.Treeview(self.top, columns=self.columns, show="headings")
        self.tree.pack(fill='both', expand=True)
        # The select button, the buttons functionality can also be acces by double clicking on mouse button 1
        self.button=tk.Button(self.top,text='Select',command=self.select)
        self.button.pack()
        self.top.bind('<Double-Button-1>', self.select)
        #The columns are set a minimum width to ensure easy readability for the header and the value
        self.tree.column(0, anchor="center", minwidth = 100)
        self.tree.column(1, anchor="center", minwidth = 50)
        self.tree.column(2, anchor="center", minwidth = 50)
        self.tree.column(3, anchor="center", minwidth = 50)
        self.tree.column(4, anchor="center", minwidth = 50)
        self.tree.column(5, anchor="center", minwidth = 50)
        self.tree.column(6, anchor="center", minwidth = 50)
        #Calls the building of the treeview widget        
        self._build_tree()
        
    def _build_tree(self):
        """
        This function builds the tree and populates it with the values in the globaly defined pre_selection_list, from the FunctionLibrary class 
        RT selection function. This gives the user the overview of how the individual sequence indentifications values 
        Furthermore it contains the possibility to adjust the column width to the len of the column header strings
        """
        for col in self.columns:
            self.tree.heading(col, text=col.title())
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title())) 
        for item in pre_selection_list:
            self.tree.insert('', 'end', values=item)

    def select(self, event=None):
        """
        This selects the item that the cursor has been pressed on and uses the row index to retrive the RT value from the globaly defined pre_selection_list, 
        from the FunctionLibrary class, RT selection function. The RT is gloablly defined an is extracted.   
        """
        row = self.tree.selection()
        row_index =self.tree.index(row)
        global RT
        RT = pre_selection_list[row_index][3]
        self.top.destroy()

class Application(tk.Frame):
    """
    This Class is used to build up the frame/GUI of the PLGS assistant :)
    The __init__ function is called by the class calls in the end of the editor. Furthermore certain global variables are defined and created
    These are used in the following class FunctionLibrary and should not be changed since this will ceartainly break the software
    The menubar is also made in the init function     
    The CreateWidgets function is used to generate the buttons, listbox and labels for the various input/output operations of the frame/GUI
    furthermore some global variables are defined, this is done so they can be used in the sorting of the loaded PLGS files.
    """
    
    def __init__(self, root):
        """
        Class call --> Tkinter frame
        
        When the class is called the frame is initiated. The global values from the user input are made
        and defined. These values are used in the functioncs in the FunctionLibrary Class. 
        """
        tk.Frame.__init__(self, root)        
        #Scrollbar and startup geometry      
        self.canvas = tk.Canvas(root, width = 1070, height = 722, borderwidth=0, background="gray94")
        self.frame = tk.Frame(self.canvas, background="gray94")
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4),window=self.frame, anchor="nw", tags="self.frame")
        self.frame.bind("<Configure>", self.OnFrameConfigure)
        self.frame.focus_force()
        #To allow the Popwindow to be a toplevel frame
        self.root = root
        #Initiating the widgets
        self.createWidgets()
        # Global variables are defined to be manipulated and transfered between Class's/Functions's
        #PLGS, The key and location lists are used in the cvs_parser function in the FunctionLibrary class
        global filelocation_list    
        filelocation_list = []
        global key_list
        key_list = []
        global protein_identifiers # Used to show the protein identifiers in the protein identifier listbox
        protein_identifiers = []
        global added_identifiers
        added_identifiers = set()
        # Menu constructor
        self.menubar = tk.Menu(self)
        #Help Menu
        menu = tk.Menu(self.menubar)        
        menu.add_command(label = "Save", command = self.save)
        menu.add_command(label = "Load", command = self.load)
        menu.add_command(label = "About", command = self.About)
        self.menubar.add_cascade(label = "File", menu = menu)
        root.config(menu = self.menubar)
        self.Dialog_insert("Hi there friend.\nThis is where i am going to show you the results of your LARS analysis.\nIf something goes wrong i should be able to help you fix it.\n\n")
    
    def createToolTip(widget, text):
        """
        Call the functions within the ToolTip class and modifies the text so it reflect the widget
        """
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def OnFrameConfigure(self, event):
        '''
        Reset the scroll region to encompass the inner frame.
        '''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def RT_Selection_popup(self):
        """
        This function makes sure that the RT_Selection_Treeview class is a toplevel window of the main GUI class
        """
        self.RT_window=RT_Selection_Treeview(root)
        root.wait_window(self.RT_window.top)
       
    def createWidgets(self): 
        """
        All the widgets that are present when the frame is started are defined below. 
        """
                
        #The textbox for keeping track of the program's progress
        global Dialog
        Dialog_scrollbar = tk.Scrollbar(self.frame)
        Dialog_scrollbar.grid(row=13, column=7, rowspan =5, sticky='n,s')
        Dialog = tk.Text(self.frame, height = 11, relief = 'groove', bd = 2, width = 80, yscrollcommand=Dialog_scrollbar.set)
        Dialog.grid(column = 3, row = 13, columnspan = 4, rowspan = 5, sticky = "n,e", padx = 5, pady = 5)
        Dialog_scrollbar.config(command=Dialog.yview)
        Dialog.config(state=tk.DISABLED) #The box is keept in active so the user cannot write anything into it
        
        #The listbox for the PLGS file upload        
        self.listbox_PLGS = tk.Listbox(self.frame, height = 12, width = 62, bd = 3, relief = "groove")
        self.listbox_PLGS.grid(column = 0, row = 0, rowspan = 5, columnspan = 3, padx = 5, pady = 5)
        #The listbox for the Protein Identifiers
        self.listbox_Protein_Identifier = tk.Listbox(self.frame, height = 12, width = 62, bd = 3, relief = "groove")
        self.listbox_Protein_Identifier.grid(column = 0, row = 6, rowspan = 5, columnspan = 2, padx = 5, pady = 5) 
        #The add PLGS button
        self.button_add = tk.Button(self.frame, text = "Add an Ion Accounting File", command = self.Add_PLGS)
        self.button_add.grid(column = 0, row = 5, padx = 5, pady = 5, sticky = "n, w",)
        #The remove PLGS button        
        self.button_remove = tk.Button(self.frame, text = "Remove an Ion Accounting File", command = self.Delete_PLGS)
        self.button_remove.grid(column = 1, row = 5, padx = 5, pady = 5, sticky = "n, w",)
        #The process button        
        self.button_process = tk.Button(self.frame, text = "Run the LARS processing", command = self.Process)
        self.button_process.grid(column = 0, row = 15, padx = 5, pady = 5, sticky = "n, w")
        createToolTip(self.button_process, "Start the Scoring and Sorting of the Ion accounting files. You will be prompted to make a folder,\nall of the processing output is stored here")
        #The Update button        
        self.button_pre_process = tk.Button(self.frame, text = "Update", command = self.Pre_Process)
        self.button_pre_process.grid(column = 3, row = 5, padx = 5, pady = 5, sticky = "n,e")
        createToolTip(self.button_pre_process, "Test the sorting abilities of your current values")
        #The header for the filter section
        self.FilterHeader = tk.Label(self.frame, text = "Insert your filter values")
        self.FilterHeader.grid(column = 3, row = 0, sticky = "n, w", padx = 5, pady = 5)
               
        #The cutoff text        
        self.cutoff = tk.Label(self.frame, text = "Cut-off value    ")
        self.cutoff.grid(column = 4, row = 5, sticky = "n, e", padx = 5, pady = 5)
        createToolTip(self.cutoff,"Values lower or not meeting your selection\nwill be excluded from further treatment")
        self.Scrcutoff= tk.Label(self.frame, text = "Minimum scoring value")
        self.Scrcutoff.grid(column = 5, row = 5, sticky = "n, e", padx = 5, pady = 5)
        createToolTip(self.Scrcutoff,"Values meeting or exceeding your selection grants a point")
        
        #Value labels and boxes
        #The protein identifier entry     
        Protien_identifier_str = tk.StringVar()
        self.ProteinIdentifier_Entry = tk.Entry(self.frame, width=50)
        self.ProteinIdentifier_Entry.grid(column = 4, columnspan = 2, row = 1, sticky = "n, w", padx = 5, pady = 5)
        self.ProteinIdentifier_Label = tk.Label(self.frame, text = "Protein Identifier")
        self.ProteinIdentifier_Label.grid(column = 3, row = 1, sticky = "n, w", padx = 5, pady = 5)
        self.ProteinIdentifier_Entry.insert(0, string = "No protein identifier has been selected")
        #createToolTip(self.ProteinIdentifier_Entry, "The Protein identifier is the name given\n when creating the PLGS database")        
        #The Maximum MH+ Error (ppm) Entry
        self.MaximumMHErrorPPM_Entry = tk.Entry(self.frame, width=50)
        self.MaximumMHErrorPPM_Entry.grid(column = 4, columnspan = 2, row = 2, sticky = "n,w", padx = 5, pady = 5)
        self.MaximumMHErrorPPM_Label = tk.Label(self.frame, text = "Maximum MH+ Error (ppm)")
        self.MaximumMHErrorPPM_Label.grid(column = 3, row = 2, sticky = "n,w", padx = 5, pady = 5)
        self.MaximumMHErrorPPM_Entry.insert(0,10)
        #The Minimum Sequence length Entry
        self.MinimumSequenceLength_Entry = tk.Entry(self.frame, width=50)
        self.MinimumSequenceLength_Entry.grid(column = 4, columnspan = 2, row = 3, sticky = "n, w", padx = 5, pady = 5)
        self.MinimumSequenceLength_Label = tk.Label(self.frame, text="Minimum Sequence Length")
        self.MinimumSequenceLength_Label.grid(column = 3, row = 3, sticky = "n, w", padx = 5, pady = 5)
        self.MinimumSequenceLength_Entry.insert(0,7)
        #The Maximum Sequence legnth Entry        
        self.MaximumSequenceLength_Entry = tk.Entry(self.frame, width=50)
        self.MaximumSequenceLength_Entry.grid(column = 4, columnspan = 2, row = 4, sticky = "n, w", padx = 5, pady = 5)
        self.MaximumSequenceLength_Label = tk.Label(self.frame, text = "Maximum Sequence Length")
        self.MaximumSequenceLength_Label.grid(column = 3, row = 4, sticky = "n, w", padx = 5, pady = 5)
        self.MaximumSequenceLength_Entry.insert(0, 55)
        #The minimum intensity entry
        self.MinimumIntensity_Entry = tk.Entry(self.frame)
        self.MinimumIntensity_Entry.grid(column = 4, row = 6, sticky = "n, w", padx = 5, pady = 5)
        self.MinimumIntensity_Label = tk.Label(self.frame, text = "Minimum Intensity")
        self.MinimumIntensity_Label.grid(column = 3, row = 6, sticky = "n, w", padx = 5, pady = 5)
        self.MinimumIntensity_Entry.insert(0, 0)
        #The Minimum products Entry
        self.MinimumProducts_Entry = tk.Entry(self.frame)
        self.MinimumProducts_Entry.grid(column = 4, row = 7, sticky = "n, w", padx = 5, pady = 5)
        self.MinimumProducts_Label = tk.Label(self.frame, text = "Minimum Products")
        self.MinimumProducts_Label.grid(column = 3, row = 7, sticky = "n, w", padx = 5, pady = 5)
        self.MinimumProducts_Entry.insert(0, 0)
        #The minimum products per amino acid Entry
        self.MinimumProductsPerAminoAcid_Entry = tk.Entry(self.frame)
        self.MinimumProductsPerAminoAcid_Entry.grid(column = 4, row = 8, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumProductsPerAminoAcid_Label = tk.Label(self.frame, text = "Minimum Products Per Amino Acid")
        self.MinimumProductsPerAminoAcid_Label.grid(column = 3, row = 8, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumProductsPerAminoAcid_Entry.insert(0, 0)
        #The minimum Consecutive Products Entry
        self.MinimumConsecutiveProducts_Entry = tk.Entry(self.frame)
        self.MinimumConsecutiveProducts_Entry.grid(column = 4, row = 9, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumConsecutiveProducts_Label = tk.Label(self.frame, text = "Minimum Consecutive Products")
        self.MinimumConsecutiveProducts_Label.grid(column = 3, row = 9, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumConsecutiveProducts_Entry.insert(0, 0)
        #The minimum int sum of indentified products
        self.MinimumProdIntSum_Entry = tk.Entry(self.frame)
        self.MinimumProdIntSum_Entry.grid(column = 4, row = 10, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumProdIntSum_Label = tk.Label(self.frame, text = "Minimum Sum for Identified Products")
        self.MinimumProdIntSum_Label.grid(column = 3, row = 10, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumProdIntSum_Entry.insert(0, 0)
        #The minimum score entry
        self.MinimumScore_Entry = tk.Entry(self.frame)
        self.MinimumScore_Entry.grid(column = 4, row = 11, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumScore_Label = tk.Label(self.frame, text = "Minimum Peptide Score")
        self.MinimumScore_Label.grid(column = 3, row = 11, sticky = "n,w", padx = 5, pady = 5)
        self.MinimumScore_Entry.insert(0, 0)
        #The Number of identifications meeting filter criteria's Entry
        self.NoOffReplicates_Entry = tk.Entry(self.frame)
        self.NoOffReplicates_Entry.grid(column = 4, row = 12, sticky = "n,w", padx = 5, pady = 5)
        self.NoOffReplicates_Label = tk.Label(self.frame, text = "Minimum Number of Replicates")
        self.NoOffReplicates_Label.grid(column = 3, row = 12, sticky = "n,w", padx = 5, pady = 5)
        self.NoOffReplicates_Entry.insert(0, 0)
        
        # Score header
        self.ScrMinimumIntensity_Entry = tk.Entry(self.frame)        
        self.ScrMinimumIntensity_Entry.grid(column = 5, row = 6, sticky = "n, e", padx = 5, pady = 5)
        self.ScrMinimumIntensity_Entry.insert(0, 1000)
        self.ScrMinimumProducts_Entry = tk.Entry(self.frame)
        self.ScrMinimumProducts_Entry.grid(column = 5, row = 7, sticky = "n, e", padx = 5, pady = 5)
        self.ScrMinimumProducts_Entry.insert(0, 2)
        self.ScrMinimumProductsPerAminoAcid_Entry = tk.Entry(self.frame)
        self.ScrMinimumProductsPerAminoAcid_Entry.grid(column = 5, row = 8, sticky = "n,e", padx = 5, pady = 5)
        self.ScrMinimumProductsPerAminoAcid_Entry.insert(0, 0.15)        
        self.ScrMinimumConsecutiveProducts_Entry = tk.Entry(self.frame)
        self.ScrMinimumConsecutiveProducts_Entry.grid(column = 5, row = 9, sticky = "n,e", padx = 5, pady = 5)
        self.ScrMinimumConsecutiveProducts_Entry.insert(0, 1)
        self.ScrMinimumProdIntSum_Entry = tk.Entry(self.frame)
        self.ScrMinimumProdIntSum_Entry.grid(column = 5, row = 10, sticky = "n,e", padx = 5, pady = 5)
        self.ScrMinimumProdIntSum_Entry.insert(0, 500)
        self.ScrMinimumScore_Entry = tk.Entry(self.frame)
        self.ScrMinimumScore_Entry.grid(column = 5, row = 11, sticky = "n,e", padx = 5, pady = 5)
        self.ScrMinimumScore_Entry.insert(0, 6.4)
        self.ScrNoOffReplicates_Entry = tk.Entry(self.frame)
        self.ScrNoOffReplicates_Entry.grid(column = 5, row = 12, sticky = "n,e", padx = 5, pady = 5)
        self.ScrNoOffReplicates_Entry.insert(0, 2)                  
        
        #Score overview
        self.ScrOvw_Header = tk.Label(self.frame,text = "Sequence Passes")
        self.ScrOvw_Header.grid(column = 6, row = 5, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_MinimumIntenstity=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_MinimumIntenstity.grid(column = 6, row = 6, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_ScrMinimumProducts=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_ScrMinimumProducts.grid(column = 6, row = 7, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_ScrMinimumProductsPerAminoAcid=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_ScrMinimumProductsPerAminoAcid.grid(column = 6, row = 8, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_ScrMinimumConsecutiveProducts=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_ScrMinimumConsecutiveProducts.grid(column = 6, row = 9, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_ScrMinimumProdIntSum=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_ScrMinimumProdIntSum.grid(column = 6, row = 10, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_ScrMinimumScore=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_ScrMinimumScore.grid(column = 6, row = 11, sticky = "n, e", padx = 5, pady = 5)
        self.ScrOvw_ScrNoOffReplicates=tk.Label(self.frame, text="Press Update")
        self.ScrOvw_ScrNoOffReplicates.grid(column = 6, row = 12, sticky = "n, e", padx = 5, pady = 5)
        
        #The minimum sequence score
        self.MinSeqScr_Entry = tk.Entry(self.frame, width = 5)
        self.MinSeqScr_Entry.grid(column = 1, row = 13, sticky = "n,w", padx = 5, pady = 5)
        self.MinSeqScr_Label = tk.Label(self.frame, text = "The minimum sequence score (0-7)")
        self.MinSeqScr_Label.grid(column = 0, row = 13, sticky = "n,w", padx = 5, pady = 5)
        self.MinSeqScr_Entry.insert(0, 4)
        createToolTip(self.MinSeqScr_Entry, "Set the lowest score that will be incorporated into the output files")
        #Allowed RT SD
        self.RT_SD_Entry = tk.Entry(self.frame, width = 5)
        self.RT_SD_Entry.grid(column = 1, row = 14, sticky = "n,w", padx = 5, pady = 5)
        self.RT_SD_Label = tk.Label(self.frame, text = "Maximum allowed RT SD")
        self.RT_SD_Label.grid(column = 0, row = 14, sticky = "n,w", padx = 5, pady = 5)  
        self.RT_SD_Entry.insert(0, 0.5)
        createToolTip(self.RT_SD_Entry, "Set the max standard deviation for the retention time for a peptide identification.\nFor peptides exceeding this, the user will be prompted to make a decision")
        
        #Select a protein identifier
        self.Protein_Identifier_Select = tk.Button(self.frame, text = "Select Protein Identifier" ,command = self.Select_Protein_identfier)
        self.Protein_Identifier_Select.grid(column = 0, row = 11, sticky = "n,w", padx = 5, pady = 5 )
        self.listbox_Protein_Identifier.bind('<Double-1>', lambda x: self.Protein_Identifier_Select.invoke())
        
    def Dialog_insert(self, text):
        """
        text --> text inserted in a dialogbox
        
        This function is used to insert text into the dialogbox in the base GUI. The function works by unlocking the dialog box,
        inserting the desired text and closes the box for further input
        """
        Dialog.config(state=tk.NORMAL)
        Dialog.insert(tk.END, text)
        Dialog.see(tk.END)
        Dialog.config(state=tk.DISABLED)
    
    
    def Get(self):
        """
        This functions purpose is to extract the values typed into the entry boxes, and make sure that 
        """
        #Block Start
        #Gets the Protein Identifier from the entry box and Tests whether or not it can be used
        global Prot_ident        
        Prot_ident = self.ProteinIdentifier_Entry.get()
        if type(Prot_ident) is str:
            pass
        else:
            self.Dialog_insert("The Protein identifier is not a string, use the select Protein Identifier window.\nRun aborted\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the cutoff minimum intensity from the entry box and Tests whether or not it can be used
        global MinInt        
        s = self.MinimumIntensity_Entry.get()
        try: 
            MinInt = int(s)
        except:
            self.Dialog_insert("The Cutoff minimun intensity is not an integer.\nIt should be a whole number like 1000.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the score minimum intensity from the entry box and Tests whether or not it can be used
        global ScrMinInt        
        s = self.ScrMinimumIntensity_Entry.get()
        try: 
            ScrMinInt = int(s)
        except:
            self.Dialog_insert("The Score minimun intensity is not an integer.\nIt should be a whole number like 1000.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the minimum seqeunce length  from the entry box and Tests whether or it not can be used
        global MinSeqLen       
        s = self.MinimumSequenceLength_Entry.get()
        try: 
            MinSeqLen = int(s)
        except:
            self.Dialog_insert("The minimun sequence length is not an integer.\nIt should be a whole number like 7.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the maximum seqeunce length  from the entry box and Tests whether or it not can be used
        global MaxSeqLen        
        s = self.MaximumSequenceLength_Entry.get()
        try: 
            MaxSeqLen = int(s)
        except:
            self.Dialog_insert("The maximum sequence length is not an integer.\nIt should be a whole number like 30.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the cutoff minimum product from the entry box and Tests whether or it not can be used
        global MinProd      
        s = self.MinimumProducts_Entry.get()
        try: 
            MinProd = int(s)
        except:
            self.Dialog_insert("The cutoff minimum product is not not an integer.\nIt should be a whole number like 1.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Score minimum product from the entry box and Tests whether or it not can be used
        global ScrMinProd      
        s = self.ScrMinimumProducts_Entry.get()
        try: 
            ScrMinProd = int(s)
        except:
            self.Dialog_insert("The Score minimum product is not not a integer.\nIt should be a whole number like 1.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the cutoff minimum products per amino acid from the entry box and Tests whether or it not can be used
        global MinProdPAA        
        s = self.MinimumProductsPerAminoAcid_Entry.get()
        try: 
            MinProdPAA = float(s)
        except:
            self.Dialog_insert("The Cutoff minimum products per amino acid is not not a float.\nIt should be a whole number like 1 or a decimal like 1.2.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the score minimum products per amino acid from the entry box and Tests whether or it not can be used
        global ScrMinProdPAA        
        s = self.ScrMinimumProductsPerAminoAcid_Entry.get()
        try: 
            ScrMinProdPAA = float(s)
        except:
            self.Dialog_insert("The Score minimum products per amino acid is not not a float.\nIt should be a whole number like 1 or a decimal like 1.2.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the cutoff minimum consecutive products from the entry box and Tests whether or not it can be used
        global MinConProd        
        s = self.MinimumConsecutiveProducts_Entry.get()
        try: 
            MinConProd = int(s)
        except:
            self.Dialog_insert("The Cutoff mminimum consecutive products is not not an integer.\nIt should be a whole number like 1.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Score minimum consecutive products from the entry box and Tests whether or not it can be used
        global ScrMinConProd        
        s = self.ScrMinimumConsecutiveProducts_Entry.get()
        try: 
            ScrMinConProd = int(s)
        except:
            self.Dialog_insert("The Score mminimum consecutive products is not not an integer.\nIt should be a whole number like 1.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Cutoff minimum product sum intensity from the entry box and Tests whether or not it can be used
        global MinProdSum
        s= self.MinimumProdIntSum_Entry.get()
        try: 
            MinProdSum = int(s)
        except:
            self.Dialog_insert("The Cutoff minimum product sum intensity is not not an integer.\nIt should be a whole number like 100.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Score minimum product sum intensity from the entry box and Tests whether or not it can be used
        global ScrMinProdSum
        s= self.ScrMinimumProdIntSum_Entry.get()
        try: 
            ScrMinProdSum = int(s)
        except:
            self.Dialog_insert("The Score minimum product sum intensity is not not an integer.\nIt should be a whole number like 100.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Cutoff minimum peptide Score from the entry box and Tests whether or not it can be used
        global MinScr        
        s = self.MinimumScore_Entry.get()
        try: 
            MinScr = float(s)
        except:
            self.Dialog_insert("The Cutoff minimum peptide Score is not not a float.\nIt should be a whole number like 5 or a decimal like 5.4.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Score minimum peptide Score from the entry box and Tests whether or not it can be used
        global ScrMinScr        
        s = self.ScrMinimumScore_Entry.get()
        try: 
            ScrMinScr = float(s)
        except:
            self.Dialog_insert("The Score minimum peptide Score is not not a float.\nIt should be a whole number like 5 or a decimal like 5.4.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the maximum mass error from the entry box and Tests whether or not it can be used
        global MaxMHHErr        
        s = self.MaximumMHErrorPPM_Entry.get()
        try: 
            MaxMHHErr = int(s)
        except:
            self.Dialog_insert("The maximum mass error is not not an integer.\nIt should be a whole number like 5.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the cutoff number of replicates from the entry box and Tests whether or not it can be used
        global NoOffRep        
        s = self.NoOffReplicates_Entry.get()
        try: 
            NoOffRep = int(s)
        except:
            self.Dialog_insert("The cutoff number of replicates is not not an integer.\nIt should be a whole number like 2.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Score number of replicates from the entry box and Tests whether or not it can be used
        global ScrNoOffRep        
        s = self.ScrNoOffReplicates_Entry.get()
        try: 
            ScrNoOffRep = int(s)
        except:
            self.Dialog_insert("The Score number of replicates is not not an integer.\nIt should be a whole number like 2.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Minimum sequence score from the entry box and Tests whether or not it can be used
        global MinSeqScr       
        s = self.MinSeqScr_Entry.get()
        try: 
            MinSeqScr = int(s)
        except:
            self.Dialog_insert("The Minimum sequence score is not not an integer.\nIt should be a whole number like 2.\nRun Aborted.\n\n")
            raise ValueError
        #Block end
        
        #Block Start
        #Gets the Allowed Standard deviation from the entry box and Tests whether or not it can be used
        global Allowed_SD
        s = self.RT_SD_Entry.get()
        try: 
            Allowed_SD = float(s)
        except:
            self.Dialog_insert("The Allowed Standard deviation is not not an integer.\nIt should be a whole number like 2.\nRun Aborted.\n\n")
            raise ValueError
        Allowed_SD = float(s)
        #Block end        
        
    def Pre_Process(self):
        """
        This function allows for the pre determination of the sequence coverage at the different scores, the number of peptides identified and
        the average amino acid redundancy.
        """
        self.Get()
        self.dict_to_be_sorted = {}
        self.sorted_dict = {}
        self.score_dict = {}
        self.score_tracking_dict = {}
        FunctionLibrary.csv_parser(self)
        FunctionLibrary.csv_sorter(self)  
        FunctionLibrary.Score_counter(self)
        FunctionLibrary.Score_sorter_pre_process(self)
        self.changing_labels()
        
    def changing_labels(self):
        """
        Changes the labels of the scoring parameters in the score overview column
        """       
        keys = self.score_tracking_dict.keys()
        seq_set = set()
        for item in keys:
            value = self.score_tracking_dict[item]
            for ite in value:
                seq_set.add(ite[0])
        number_of_unique_sequences = len(seq_set)        
        
        for key in keys: ## Slow! Look at possible rework
            value = self.score_tracking_dict[key]
            value_len = len(value)       
            value_count = 0        
            for item in seq_set:
                pass_count = 0
                entry = 0
                while entry < value_len:
                    if item == value[entry][0]:
                        if value[entry][1] == "pass":
                            pass_count += 1
                        else:
                            pass
                    else:
                        pass
                    entry += 1
                if pass_count > 0:
                    value_count += 1
            string = "{0} out of {1}".format(value_count, number_of_unique_sequences)
            if key == 'MinInt':
                self.ScrOvw_MinimumIntenstity.config(text = string)
            elif key == 'MinProd':
                self.ScrOvw_ScrMinimumProducts.config(text = string)
            elif key == 'MinMinProdPAA':
                self.ScrOvw_ScrMinimumProductsPerAminoAcid.config(text = string)
            elif key == 'MinConProd':
                self.ScrOvw_ScrMinimumConsecutiveProducts.config(text = string)
            elif key == 'MinProdSum':
                self.ScrOvw_ScrMinimumProdIntSum.config(text = string)
            elif key == 'MinScr':
                self.ScrOvw_ScrMinimumScore.config(text = string)
            elif key == 'MinNoOffRep' :
                self.ScrOvw_ScrNoOffReplicates.config(text = string)
            else:
                print("You done fuck'ed up buddy")
            
    def Process(self):
        """
        This function determines what happens when the Process button is pressed
        When the Procces button is pressed the FunctionLibrary is called and the values typed into the boxes are stored
        """
        self.Get()
        FunctionLibrary()
        
    def save(self):
        """
        From the filemenu this function is initiated by pressing the save name in the dropdown menu
        
        The user is prompted were to save the log file. The log file is given the default extension _log.txt
        so it can, by deault, be found by the load function
        
        The date and time for the creation of the file is written in and so is the values of all the entryboxes, furthermore the filelocation and keys 
        from the PLGS files is saved so they can be loaded in
        """
        self.Get()
        self.log_loc = tk.filedialog.asksaveasfilename(defaultextension = "_log.txt")
        self.file_log = open(self.log_loc, 'w')
        date_and_time = str(datetime.datetime.now())
        self.file_log.write(date_and_time + "\n")
        self.file_log.write("{0} | {1}\n".format("The Protein Identier was set to", self.ProteinIdentifier_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off Intensity was set to", self.MinimumIntensity_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Awarding Intensity was set to", self.ScrMinimumIntensity_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off Sequence Length was set to", self.MinimumSequenceLength_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Maximum Cut-off Sequence Length was set to", self.MaximumSequenceLength_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off number of Products was set to", self.MinimumProducts_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Awarding number of Products was set to", self.ScrMinimumProducts_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off number of Products Per Amino Acid  was set to", self.MinimumProductsPerAminoAcid_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Awarding number of Products Per Amino Acid  was set to", self.ScrMinimumProductsPerAminoAcid_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off number of Consecutive Products was set to", self.MinimumConsecutiveProducts_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Awarding number of Consecutive Products was set to", self.ScrMinimumConsecutiveProducts_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off intensity sum for the identified products was set to", self.MinimumProdIntSum_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Awarding intensity sum for the identified products was set to", self.ScrMinimumProdIntSum_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off peptide Score was set to", self.MinimumScore_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Awarding peptide Score was set to", self.ScrMinimumScore_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off Mass delta Error was set to", self.MaximumMHErrorPPM_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Cut-off number of replicates was set to", self.NoOffReplicates_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum point awarding number of replicates was set to", self.ScrNoOffReplicates_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The Minimum Sequence score was set to",self.MinSeqScr_Entry.get())) 
        self.file_log.write("{0} | {1}\n".format("The allowed SD was set to", self.RT_SD_Entry.get()))
        self.file_log.write("{0} | {1}\n".format("The number of PLGS files loaded were",len(filelocation_list)))
        for item in filelocation_list:
            self.file_log.write("{0}\n".format(item))
        for item in key_list:
            self.file_log.write("{0}\n".format(item))
        self.file_log.close()
    
    def load(self):
        """
        From the filemenu this function is initiated by pressing the load name in the dropdown menu
        
        The askopenfile dialog asks for the a file with the _log.txt extension, since this will ensure a corret file format is being loaded
        
        The values from the entry boxes are first cleared and then the value from the log file is inserted, furthermore the PLGS locations and keys
        are loaded in
        
        """
        self.listbox_PLGS.delete(0,"end")
        filelocation_list.clear()
        key_list.clear()
        file_load = tk.filedialog.askopenfile(filetypes =[("txt", "_log.txt"),('All files','*.*')])        
        Regular_expression = re.compile("\w.+was set to.+ (\w.*)")
        Regular_expression2 = re.compile("\w.+loaded were.+ (\w.*)")
        lines = file_load.readlines()
        lines_clean = []
        for item in lines:
            clean = item.strip('\n')
            lines_clean.append(clean)
        # Protein identifier               
        match = re.match(Regular_expression, lines_clean[1])
        Load_value = match.group(1)
        self.ProteinIdentifier_Entry.delete(0, tk.END)
        self.ProteinIdentifier_Entry.insert(0, Load_value)
        # Minimum intensity              
        match = re.match(Regular_expression, lines_clean[2])
        Load_value = match.group(1)
        self.MinimumIntensity_Entry.delete(0, tk.END)
        self.MinimumIntensity_Entry.insert(0, Load_value)
        # Minimum Score Intensity
        match = re.match(Regular_expression, lines_clean[3])
        Load_value = match.group(1)
        self.ScrMinimumIntensity_Entry.delete(0, tk.END)
        self.ScrMinimumIntensity_Entry.insert(0, Load_value)
        # Minimum sequence length               
        match = re.match(Regular_expression, lines_clean[4])
        Load_value = match.group(1)
        self.MinimumSequenceLength_Entry.delete(0, tk.END)
        self.MinimumSequenceLength_Entry.insert(0, Load_value)
        # Maximum sequence length          
        match = re.match(Regular_expression, lines_clean[5])
        Load_value = match.group(1)
        self.MaximumSequenceLength_Entry.delete(0, tk.END)
        self.MaximumSequenceLength_Entry.insert(0, Load_value)
        # Minimum number of products               
        match = re.match(Regular_expression, lines_clean[6])
        Load_value = match.group(1)
        self.MinimumProducts_Entry.delete(0, tk.END)
        self.MinimumProducts_Entry.insert(0, Load_value)
        # Minimum Scoring number of products               
        match = re.match(Regular_expression, lines_clean[7])
        Load_value = match.group(1)
        self.ScrMinimumProducts_Entry.delete(0, tk.END)
        self.ScrMinimumProducts_Entry.insert(0, Load_value)
        # Minimum products per amino acid               
        match = re.match(Regular_expression, lines_clean[8])
        Load_value = match.group(1)
        self.MinimumProductsPerAminoAcid_Entry.delete(0, tk.END)
        self.MinimumProductsPerAminoAcid_Entry.insert(0, Load_value)
        # Minimum Scoring products per amino acid               
        match = re.match(Regular_expression, lines_clean[9])
        Load_value = match.group(1)
        self.ScrMinimumProductsPerAminoAcid_Entry.delete(0, tk.END)
        self.ScrMinimumProductsPerAminoAcid_Entry.insert(0, Load_value)
        # Minimum number of consecutive products               
        match = re.match(Regular_expression, lines_clean[10])
        Load_value = match.group(1)
        self.MinimumConsecutiveProducts_Entry.delete(0, tk.END)
        self.MinimumConsecutiveProducts_Entry.insert(0, Load_value)
        # Minimum Scoring number of consecutive products               
        match = re.match(Regular_expression, lines_clean[11])
        Load_value = match.group(1)
        self.ScrMinimumConsecutiveProducts_Entry.delete(0, tk.END)
        self.ScrMinimumConsecutiveProducts_Entry.insert(0, Load_value)
        # Minimum intensity sum for identified products               
        match = re.match(Regular_expression, lines_clean[12])
        Load_value = match.group(1)
        self.MinimumProdIntSum_Entry.delete(0, tk.END)
        self.MinimumProdIntSum_Entry.insert(0, Load_value)
        # Minimum Score intensity sum for identified products               
        match = re.match(Regular_expression, lines_clean[13])
        Load_value = match.group(1)
        self.ScrMinimumProdIntSum_Entry.delete(0, tk.END)
        self.ScrMinimumProdIntSum_Entry.insert(0, Load_value)
        # Minimum peptide Score               
        match = re.match(Regular_expression, lines_clean[14])
        Load_value = match.group(1)
        self.MinimumScore_Entry.delete(0, tk.END)
        self.MinimumScore_Entry.insert(0, Load_value)
        # Minimum scoring Score               
        match = re.match(Regular_expression, lines_clean[15])
        Load_value = match.group(1)
        self.ScrMinimumScore_Entry.delete(0, tk.END)
        self.ScrMinimumScore_Entry.insert(0, Load_value)
        # Maximum Mass delta error               
        match = re.match(Regular_expression, lines_clean[16])
        Load_value = match.group(1)
        self.MaximumMHErrorPPM_Entry.delete(0, tk.END)
        self.MaximumMHErrorPPM_Entry.insert(0, Load_value)
        # The minimum number of identifications that meet the sorting criterias                
        match = re.match(Regular_expression, lines_clean[17])
        Load_value = match.group(1)
        self.NoOffReplicates_Entry.delete(0, tk.END)
        self.NoOffReplicates_Entry.insert(0, Load_value)
        # The minimum number of identifications that meet the sorting criterias                
        match = re.match(Regular_expression, lines_clean[18])
        Load_value = match.group(1)
        self.ScrNoOffReplicates_Entry.delete(0, tk.END)
        self.ScrNoOffReplicates_Entry.insert(0, Load_value)
        # The minimum number of identifications                
        match = re.match(Regular_expression, lines_clean[19])
        Load_value = match.group(1)
        self.MinSeqScr_Entry.delete(0, tk.END)
        self.MinSeqScr_Entry.insert(0, Load_value)
        # SD cutoff limit            
        match = re.match(Regular_expression, lines_clean[20])
        Load_value = match.group(1)
        self.RT_SD_Entry.delete(0, tk.END)
        self.RT_SD_Entry.insert(0, Load_value)
        # Use of the pepsin cleavage rules
        Number_of_files_id = re.match(Regular_expression2, lines_clean[21])
        Number_of_files = int(Number_of_files_id.group(1))
        if Number_of_files == 0:
            pass
        else:
            line_counter = 22
            end_line = line_counter + Number_of_files        
            while line_counter < end_line:
                filelocation_list.append(lines_clean[line_counter])            
                line_counter += 1
            end_line = end_line + Number_of_files
            while line_counter < end_line:
                key_list.append(lines_clean[line_counter])
                self.listbox_PLGS.insert(tk.END, lines_clean[line_counter])
                line_counter += 1
        file_load.close()
    
    def About(self):
        """
        .txt file --> tkinter messagebox
        
        At this stage in the development the .txt file is hardcoded in. This will lead to an issue when
        the program is used on a different system
        
        This functions dictate the the content of the about button in the menubar information. 
        The function is actived from the menubar --> Information --> About
        """        
        about_txt = open('About.txt', 'r')
        about = about_txt.readlines()
        message = ''
        for item in about:
            message += item
        self.messagebox = messagebox.showinfo(title = "About", message = message)      
        
    def Add_PLGS(self):
        """
        This function adds a PLGS file into the listbox defined in the __init__ function.
        The loaded filelocation is changed into a normpath so it can be used in the .csv parser in
        the FunctionLibrary Class
        
        The filelocation is furthermore changed into a norm_path to make regular expression possible.
        From the norm_path the characters between the \ and  _IA_final_peptide.csv will be the name
        that shows up in the listbox. This string sequence is also used as a key in the csv_parser
        """
        Regular_expression = re.compile('(\w.*)(_IA_final_peptide.csv)')
        filelocation = tk.filedialog.askopenfilename(filetypes =[("csv","_IA_final_peptide.csv"), ('All files','*.*')])
        if filelocation == '':
            self.Dialog_insert("No ion accounting file was added file was added")# Used to inform the user and prevent an error message
        else:
            #This block changes the working directory so the user will have fewer folders to press to load their files
            dir_list = filelocation.split('/')
            working_dict = ''
            for item in dir_list[:-2]:
                if item == dir_list[-3]:
                    working_dict += item
                else:
                    working_dict += "{0}/".format(item)
            os.chdir(working_dict)
            #Block end
            #This block saves the file path into the list that is used both in the save file and in the processing functions
            path = os.path.normpath(filelocation)
            filelocation_list.append(path)
            elements_list = path.split('\\')
            pre_filename = elements_list[-1]
            match = re.match(Regular_expression, pre_filename)
            filename = match.group(1)
            key_list.append(filename)
            self.listbox_PLGS.insert(tk.END, filename)
            #Block end
            # In this block the file is read and Protein Identifiers are pulled out
            self.dict_to_be_sorted = {}
            FunctionLibrary.csv_parser(self)
            for item in protein_identifiers:
                if item in added_identifiers:
                    pass
                else:
                    self.listbox_Protein_Identifier.insert(tk.END, item)
                    added_identifiers.add(item)

    def Delete_PLGS(self):
        """
        This function is used when the Delete PLGS button is pushed
        
        This function deletes the PLGS entry from the listbox, filelocation list and key list
        """
        pre_index = self.listbox_PLGS.curselection()
        index = int(pre_index[0])
        filelocation_list.pop(index)
        key_list.pop(index)
        self.listbox_PLGS.delete(index)
    
    def Select_Protein_identfier(self):
        """
        This function allows the user to select the desired protein identfier
        """
        pre_index = self.listbox_Protein_Identifier.curselection()
        index = int(pre_index[0])
        identifier = str(protein_identifiers[index])
        self.ProteinIdentifier_Entry.delete(0, tk.END)
        self.ProteinIdentifier_Entry.insert(0, string = identifier)
        
    
class FunctionLibrary(Application, RT_Selection_Treeview):
    """
    This Class is initiated when the process button is pressed
    This function is responsible for the sorting and output of the analysis
    """
    def __init__(self):
        """
        Upon initation of the class, all the functions in the class is called.
        The necesary variables are defeined so they can be transported between the functions 
        """
        # Dictionaries that are used to transfer information between the various fuctions, information regarding the content of the dictionaries
        # can be found in the function of which the dictionaries are made                
        self.dict_to_be_sorted = {} #From csv_parser -- Used in csv_sorter
        self.sorted_dict = {} #From csv_sorter -- Used in Score_counter and Score_sorter
        self.score_dict = {} #From Score_counter -- Used in Score_sorter and Used in Score_sorter Pre_pocess 
        self.score_tracking_dict = {} #From Score_counter -- Used in Score_sorter Pre_pocess        
        self.data_mining_dict = {} #From Score_sorter -- Used in Master_list_editor
        self.master_dict = {} #From Score_sorter-- Used in master_list_editor
        self.edited_master_list = {} #From master list editor -- Used in the RT-Functions
        self.edited_master_seq_dict = {} #From master list editor -- Used in the RT-Functions
        self.final_edit = {} #From the RT-Functions -- Used in the csv_writer
        self.clean_dict = {} #From the csv_writer -- Used in helper
        # The initiation of functions needed in order to performe the analysis described in each of the functions documentation
        # Reading of the PLGS files
        self.csv_parser()
        self.Dialog_insert("The PLGS files have been loaded\n") 
        # Sorting according to PLGS values
        self.csv_sorter()  
        self.Dialog_insert("The PLGS files have been sorted\n")
        # The identifications are being scored
        self.Score_counter()
        self.Dialog_insert("The scores have been tallied\n")
        #The scores from the privous function is used to guide
        self.Score_sorter()
        self.Dialog_insert("The masterlist has been created\n")
        # This function creates the .txt file that shows the peptides sorted according to the score and contains the neccesary values in order to import the peptide
        # into dynamx
        self.Score_overview()        
        #The peptides are sorted according to number of times they are identified         
        self.Master_list_editor()   
        self.Dialog_insert("The masterlist has been cleaned and formatted\n")
        # The average RT is calculated and if the RT SD is higher than the allowed the user is prompted to select
        self.RT_User_SD_guiding_determination() 
        self.Dialog_insert("The RT of the identifications have been determined\n")
        # The .csv file is written with a user prompt were the file is saved 
        self.The_CSV_Writer() 
        self.Dialog_insert("The .csv file have been written and you have decided its location\n")
        # The function writes the .txt report 
        self.Helper_Writer() 
        self.Dialog_insert("The report has been written and the program is done\n")
        # Return to the main frame 
        self.mainloop() 
        
    def mainloop(self, n=0):
        """
        Call the mainloop of Tk.
        This is added in order to return to the main window after the .csv and .txt files have been written        
        """
        tk.mainloop(n)
    
    def csv_parser(self):
        """
        list of .csv files and keys --> dict with key calling content of csv file
        
        The file list with according keys are loaded into a dictionary where the list
        contains the header and all the values related to that header in a list.
    
        Furthermore the values that needs be either int's or float's in order to be used for selection are done so here
            
        dict[key] = [column ID, value, value, value], [column ID, value, value, value] .... [column ID, value, value, value]
        """
        Start_time = datetime.datetime.now()
        file_dict = {}
        row_list = []
        ID_list = []
        ID_and_value = []
        List_ID_and_value = []
        index_id = 0
        index_entries = 0
        number_of_files = len(filelocation_list)
        file_index = 0                              
        key_index = 0
        while file_index < number_of_files:
            filelocation = filelocation_list[file_index]
            key = key_list[key_index]
            row_list = []
            with open(filelocation) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    row_list.append(row)
            file_dict[key] = row_list
            key_index += 1
            file_index += 1
        list_of_keys = file_dict.keys()
        keys_list = []
        for key in list_of_keys:
            keys_list.append(key)
        key = keys_list[0]
        header_and_values = file_dict[key]
        header = header_and_values[0]
        number_of_IDs = len(header)
        if number_of_IDs == 63:
            index_ID_list = list(range(0,number_of_IDs))
            for index in index_ID_list:
                value = header[index_id]
                ID_list.append(value)
                index_id +=1
            index_id = 0
            for key in keys_list:
                header_and_values = file_dict[key]        
                entries = len(header_and_values)
                List_ID_and_value =[]
                index_id = 0
                while index_id < number_of_IDs:
                    while index_entries < entries:
                        value = header_and_values[index_entries][index_id]
                        if index_entries > 0:
                            #This Block is used to extract Protein Identifiers so they can be presented to the user
                            if index_id == 1:                                
                                protein_identifier = str(value)
                                if protein_identifier in protein_identifiers:
                                    pass
                                else:
                                    protein_identifiers.append(str(protein_identifier))
                            #Block End
                            elif index_id == 14: #Int sum for all identified products
                                value = float(value)
                            elif index_id == 27: #Sequence length
                                value = int(value)
                            elif index_id == 29:# Compound ID, left empty to facilitate dynamx import
                                value = ''
                            elif index_id == 30: # Number of products
                                value = int(value)
                            elif index_id == 32: # Number of consecutive products
                                value = int(value)
                            elif index_id == 35: # Peptide Score
                                value = float(value)
                            elif index_id == 37: # Mathced product sum
                                value = float(value)
                            elif index_id == 48: #The RT
                                value = float(value)
                            elif index_id == 49: #Precursor intensity
                                value = int(value)
                            elif index_id == 62:# Mass delta
                                value = float(value)
                            else:
                                pass
                        ID_and_value.append(value)
                        index_entries += 1
                    index_entries = 0
                    index_id += 1
                    List_ID_and_value.append(ID_and_value)
                    ID_and_value = []
                self.dict_to_be_sorted[key] = List_ID_and_value
        elif number_of_IDs == 65:
            index_ID_list = list(range(0,number_of_IDs))
            for index in index_ID_list:
                value = header[index_id]
                if index_id == 17:
                    pass
                elif index_id == 46:
                    pass
                else:
                    ID_list.append(value)
                index_id +=1
            index_id = 0
            for key in keys_list:
                header_and_values = file_dict[key]        
                entries = len(header_and_values)
                List_ID_and_value =[]
                index_id = 0
                while index_id < number_of_IDs:
                    if index_id == 17:
                        index_id += 1
                    elif index_id == 46:
                        index_id += 1
                    else:
                        while index_entries < entries:
                            value = header_and_values[index_entries][index_id]
                            if index_entries == 0:
                                ID_and_value.append(value)
                                index_entries += 1
                            else:
                                if index_id == 1:
                                    #This Block is used to extract Protein Identifiers so they can be presented to the user
                                    protein_identifier = str(value)
                                    if protein_identifier in protein_identifiers:
                                        pass
                                    else:
                                        protein_identifiers.append(str(protein_identifier))
                                    ID_and_value.append(protein_identifier)
                                    #Block End
                                elif index_id == 14: #Int sum for all identified products
                                    value = float(value)
                                    ID_and_value.append(value)
                                elif index_id == 17:
                                    pass
                                elif index_id == 28: #Sequence length
                                    value = int(value)
                                    ID_and_value.append(value)
                                elif index_id == 30:# Compound ID, left empty to facilitate dynamx import
                                    value = ''
                                    ID_and_value.append(value)
                                elif index_id == 31: # Number of products
                                    value = int(value)
                                    ID_and_value.append(value)
                                elif index_id == 33: # Number of consecutive products
                                    value = int(value)
                                    ID_and_value.append(value)
                                elif index_id == 36: # Peptide Score
                                    value = float(value)
                                    ID_and_value.append(value)
                                elif index_id == 38: # Mathced product sum
                                    value = float(value)
                                    ID_and_value.append(value)
                                elif index_id == 46:
                                    pass
                                elif index_id == 50: #The RT
                                    value = float(value)
                                    ID_and_value.append(value)
                                elif index_id == 51: #Precursor intensity
                                    value = int(value)
                                    ID_and_value.append(value)
                                elif index_id == 64:# Mass delta
                                    value = float(value)
                                    ID_and_value.append(value)
                                else:
                                    ID_and_value.append(value)
                            index_entries += 1
                        index_entries = 0
                        index_id += 1
                        List_ID_and_value.append(ID_and_value)
                        ID_and_value = []
                self.dict_to_be_sorted[key] = List_ID_and_value
        else:
            print("This is not a PLGS file")
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        #self.Dialog_insert("Seconds Spent in CSV_Parser {0}\n".format(difference))
        
    def csv_sorter (self):
        """
        .csv dict, sorting values --> dict with values not meeting sorting criteria excluded
        
        The csv dict gets all entries that contains a value not meeting the reqirements set
        removed. There is an inbuilt sorting of the identification that has been made by : insource, neutral_loss of H2O and NH3, 
        this is done automatically by dynamx
        
        The dictionary is further more changed from ID value list to containing each entry in
        a list.
        
        [id_index_header, id_index value, id_index value, id_index value, ...., id_index value]
        """
        Start_time = datetime.datetime.now()
        list_of_keys = self.dict_to_be_sorted.keys()
        seq_dict = {}        
        for key in list_of_keys:
            entries = 1
            size = len(self.dict_to_be_sorted[key][0])
            while entries < size:
                seq = self.dict_to_be_sorted[key][24][entries]                
                if seq in seq_dict:
                    count = seq_dict[seq]
                    new_count = count + 1
                    seq_dict[seq] = new_count
                else:
                    seq_dict[seq] = 1
                entries += 1
        for key in list_of_keys:
            size = len(self.dict_to_be_sorted[key][0])
            entries = 1
            pop_list = []  
            while entries < size:
                value = self.dict_to_be_sorted[key][1][entries]
                if value != Prot_ident:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][21][entries]
                banset = set(["InSource","NeutralLoss_H2O","NeutralLoss_NH3"])
                if value in banset:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][27][entries]
                if value > MaxSeqLen or value < MinSeqLen:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][62][entries]
                if value > MaxMHHErr or value < -MaxMHHErr:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][37][entries]
                if value < MinProdSum:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                seq = self.dict_to_be_sorted[key][24][entries]
                seq_count = seq_dict[seq]
                if seq_count < NoOffRep :
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][30][entries]
                if value < MinProd:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:        
                SeqLen = self.dict_to_be_sorted[key][27][entries]
                NoProd = self.dict_to_be_sorted[key][30][entries]
                if NoProd == 0 and MinProd == 0:
                    pass
                elif NoProd == 0:
                    pass
                else:
                    value = NoProd/SeqLen
                    if value < MinProdPAA:
                        pop_list.append(entries)
                    else:
                        pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][32][entries]
                if value < MinConProd:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:
                value = self.dict_to_be_sorted[key][35][entries]
                if value < MinScr:
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            while entries < size:      
                value = self.dict_to_be_sorted[key][49][entries]
                if value < MinInt :
                    pop_list.append(entries)
                else:
                    pass
                entries += 1
            entries = 1
            pop_list = set(pop_list)
            Number_of_IDs = len(self.dict_to_be_sorted[key])
            ID_index = 0
            Entry_index = 0
            sorted_id_and_value_list= []
            sorted_id_and_value=[]
            while ID_index < Number_of_IDs:
                while Entry_index < size:
                    if Entry_index in pop_list:
                        Entry_index += 1
                    else:
                        value = self.dict_to_be_sorted[key][ID_index][Entry_index]
                        sorted_id_and_value.append(value)
                        Entry_index += 1
                sorted_id_and_value_list.append(sorted_id_and_value)
                sorted_id_and_value=[]
                Entry_index = 0
                ID_index += 1
            self.sorted_dict[key] = sorted_id_and_value_list
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        if len(self.sorted_dict[key][1]) == 1:
            self.Dialog_insert("The Protein Identifier is not found in the added Ion Accounting files\n")
        #self.Dialog_insert("Seconds Spent in CSV_Sorter {0}\n".format(difference))
            
    def Score_counter(self):
        """
        Empty_dict -> score containing dict
        
        For each time a given sequence identification (entry) meets a criteria a point is awarded. All the points are tallied into a final score
        The score is paired with its entry and saved in a dictionary with the given file as key. A dictionary is created with the information for which entires
        fail and pass a given scoring parameter
        """
        Start_time = datetime.datetime.now()
        list_of_keys = self.sorted_dict.keys()
        MinProdSum_list = []
        MinNoOffRep_list = []
        MinProd_list = []
        MinMinProdPAA_list = []
        MinConProd_list = []
        MinScr_list = []
        MinInt_list =[]
        seq_dict = {}        
        for key in list_of_keys:
            entries = 1
            size = len(self.sorted_dict[key][0])
            while entries < size:
                seq = self.sorted_dict[key][24][entries]                
                if seq in seq_dict:
                    count = seq_dict[seq]
                    new_count = count + 1
                    seq_dict[seq] = new_count
                else:
                    seq_dict[seq] = 1
                entries += 1
        for key in list_of_keys:
            entry_score_list = []
            size = len(self.sorted_dict[key][0])
            entries = 1
            while entries < size:
                entry_score = 0
                value = self.sorted_dict[key][37][entries]
                if value < ScrMinProdSum:
                    status = "fail"
                else:
                    entry_score += 1
                    status ="pass"
                seq = self.sorted_dict[key][24][entries]
                MinProdSum_list.append((seq,status))
                seq_count = seq_dict[seq]
                if seq_count < ScrNoOffRep :
                    status = "fail"
                else:
                    status = "pass"
                    entry_score += 1
                MinNoOffRep_list.append((seq,status))
                value = self.sorted_dict[key][30][entries]
                if value < ScrMinProd:
                    status = "fail"
                else:
                    status = "pass"
                    entry_score += 1
                MinProd_list.append((seq,status))
                SeqLen = self.sorted_dict[key][27][entries]
                NoProd = self.sorted_dict[key][30][entries]
                if NoProd == 0 and ScrMinProd == 0:
                    status = "pass"
                    entry_score += 1
                elif NoProd == 0:
                    status = "fail"
                else:
                    value = SeqLen/NoProd
                    if value < ScrMinProdPAA:
                        status = "fail"
                    else:
                        status = "pass"
                        entry_score += 1
                MinMinProdPAA_list.append((seq,status))
                value = self.sorted_dict[key][32][entries]
                if value < ScrMinConProd:
                    status = "fail"
                else:
                    status = "pass"
                    entry_score += 1
                MinConProd_list.append((seq,status))
                value = self.sorted_dict[key][35][entries]
                if value < ScrMinScr:
                    status = "fail"
                else:
                    status = "pass"
                    entry_score += 1
                MinScr_list.append((seq,status))
                value = self.sorted_dict[key][49][entries]
                if value < ScrMinInt :
                    status = "fail"
                else:
                    status = "pass"
                    entry_score += 1
                MinInt_list.append((seq,status))
                entry_score_list.append((entries,entry_score))
                entries += 1                
            self.score_dict[key] = entry_score_list
        self.score_tracking_dict['MinProdSum'] = MinProdSum_list
        self.score_tracking_dict['MinNoOffRep'] = MinNoOffRep_list
        self.score_tracking_dict['MinProd'] = MinProd_list
        self.score_tracking_dict['MinMinProdPAA'] = MinMinProdPAA_list
        self.score_tracking_dict['MinConProd'] = MinConProd_list
        self.score_tracking_dict['MinScr'] = MinScr_list
        self.score_tracking_dict['MinInt'] = MinInt_list
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        #self.Dialog_insert("Seconds Spent in Score_counter {0}\n".format(difference))
    
    def Score_sorter_pre_process(self):### Currently very slow
        """
        Dict -> Dialog report
        
        The sequences are sorted acording to their score. The number of sequences assigned to each score level and the corresponding sequence coverage
        is reported to the user interface. A total number of peptides and the sequence coverage dependent on the user selected score interval
        ## Inclusion of the average amino acid redundancy 
        Dublicated sequences are removed. 
        
        """
        Start_time = datetime.datetime.now()
        score_7 = []
        score_6 = []
        score_5 = []
        score_4 = []
        score_3 = []
        score_2 = []
        score_1 = []
        score_0 = []
        
        list_of_keys = self.score_dict.keys()
        for key in list_of_keys:
            entry_score_list = self.score_dict[key]
            for item in entry_score_list:
                if item[1] == 7:
                    score_7.append((key,item[0]))
                elif item[1] == 6:
                    score_6.append((key,item[0]))
                elif item[1] == 5:
                    score_5.append((key,item[0]))
                elif item[1] == 4:
                    score_4.append((key,item[0]))
                elif item[1] == 3:
                    score_3.append((key,item[0]))
                elif item[1] == 2:
                    score_2.append((key,item[0]))
                elif item[1] == 1:
                    score_1.append((key,item[0]))
                elif item[1] == 0:
                    score_0.append((key,item[0]))
        score_list = [score_0 ,score_1, score_2, score_3, score_4, score_5, score_6, score_7]
        score_level = 7
        global Pre_process_report
        Pre_process_report = []
        Segment_list = []
        seq_coverage = 0
        for ite in score_list:
            for item in ite:
                sequence_start = int(self.sorted_dict[item[0]][26][item[1]])
                seq_length = int(self.sorted_dict[item[0]][27][item[1]]) + sequence_start                           
                segment = list(range(sequence_start, seq_length))
                Segment_list.append(segment) 
        seq_start_list = []
        seq_end_list = []
        for item in Segment_list:
            seq_start_list.append(item[0])
            seq_end_list.append(item[-1])
        starting_point = min(seq_start_list)
        end_point = max(seq_end_list)
        
        Segment_list = []        
        while score_level >= 0:            
            for item in score_list[score_level]:
                sequence_start = int(self.sorted_dict[item[0]][26][item[1]])
                seq_length = int(self.sorted_dict[item[0]][27][item[1]]) + sequence_start                           
                segment = tuple(range(sequence_start, seq_length))
                Segment_list.append(segment)
            value_list = set()
            for item in Segment_list:
                for value in item:
                    if value in value_list:
                        pass
                    else:
                        value_list.add(value)
            protein_range = list(range(starting_point,end_point+1))
            found_list = []
            for item in value_list:
                if item in protein_range:
                    found_list.append(item)
                else:
                    pass
            number_found = len(found_list)
            if number_found == 0:
                seq_coverage = 0
            else:
                seq_coverage = number_found/len(protein_range) * 100   
            number_of_peptides = len(set(Segment_list))           
            redundancy_list = []
            for item in found_list:
                times_aa_found = 0
                for ite in Segment_list:
                    for it in ite:
                        if item == it:
                            times_aa_found += 1
                        else:
                            pass
                redundancy_list.append(times_aa_found)
            redundancy_sum = 0
            if number_found == 0:
                self.redundancy = 0
            else:
                for item in redundancy_list:
                    redundancy_sum += item
                self.redundancy = float(redundancy_sum/(number_found*2))
            Pre_process_report.append((score_level,seq_coverage, number_of_peptides, self.redundancy))
            score_level -= 1
        header_string = "{0:<12}   {1:>15}   {2:>16}   {3:>13}\n".format("Score cut-off","Sequence coverage", "Number of peptides", "Redundancy")
        self.Dialog_insert(header_string)
        for item in Pre_process_report:
            seq_cov_adjust = "{0:2.1f}".format(item[1])
            redundancy_adjust ="{0:2.2f}".format(item[3])
            string = "{0:>13} {1:>18}{2} {3:>20} {4:>15}\n".format(item[0],seq_cov_adjust,"%",item[2], redundancy_adjust)
            self.Dialog_insert(string)
        self.Dialog_insert("\n")
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        #self.Dialog_insert("Seconds Spent in Score_sorter_pre_process {0}\n".format(difference))
        
    def Score_sorter(self): ## Slow
        """
        Dict -> Dict
        
        The sequences are sorted acording to their score. If the user elects to use the seqeunce coverage cut-off, when the seqeunce coverage is 100% 
        no more sequences are added. The user can determine the lowest score allowed. 
        Dublicated sequences are removed. 
        
        """
        Start_time = datetime.datetime.now()
        score_7 = []
        score_6 = []
        score_5 = []
        score_4 = []
        score_3 = []
        score_2 = []
        score_1 = []
        score_0 = []
        
        list_of_keys = self.score_dict.keys()
        for key in list_of_keys:
            entry_score_list = self.score_dict[key]
            for item in entry_score_list:
                if item[1] == 7:
                    score_7.append((key,item[0]))
                elif item[1] == 6:
                    score_6.append((key,item[0]))
                elif item[1] == 5:
                    score_5.append((key,item[0]))
                elif item[1] == 4:
                    score_4.append((key,item[0]))
                elif item[1] == 3:
                    score_3.append((key,item[0]))
                elif item[1] == 2:
                    score_2.append((key,item[0]))
                elif item[1] == 1:
                    score_1.append((key,item[0]))
                elif item[1] == 0:
                    score_0.append((key,item[0]))
        score_list = [score_0 ,score_1, score_2, score_3, score_4, score_5, score_6, score_7]
        score_level = 7
        Segment_list = []
        self.seq_coverage = 0
        for ite in score_list:
            for item in ite:
                sequence_start = int(self.sorted_dict[item[0]][26][item[1]])
                seq_length = int(self.sorted_dict[item[0]][27][item[1]]) + sequence_start                           
                segment = list(range(sequence_start, seq_length))
                Segment_list.append(segment) 
        seq_start_list = []
        seq_end_list = []
        for item in Segment_list:
            seq_start_list.append(item[0])
            seq_end_list.append(item[-1])
        starting_point = min(seq_start_list)
        end_point = max(seq_end_list)
        while score_level >= MinSeqScr:
            if self.seq_coverage == 100 and Use_seq_cutoff == 1:
                score_level -= 1
            else:
                for item in score_list[score_level]:
                    sequence_start = int(self.sorted_dict[item[0]][26][item[1]])
                    seq_length = int(self.sorted_dict[item[0]][27][item[1]]) + sequence_start                           
                    segment = list(range(sequence_start, seq_length))
                    Segment_list.append(segment)
                value_list = set()
                for item in Segment_list:
                    for value in item:
                        if value in value_list:
                            pass
                        else:
                            value_list.add(value)
                protein_range = list(range(starting_point,end_point+1))
                found_list = []
                for item in value_list:
                    if item in protein_range:
                        found_list.append('x')
                    else:
                        pass
                number_found = len(found_list)
                self.seq_coverage = number_found/len(protein_range) * 100
                
                redundancy_list = []
                for item in found_list:
                    count = 0
                    for ite in Segment_list:
                        for it in ite:
                            if it == item:
                                count += 1
                    redundancy_list.append((item,count))
                No_ids = 0
                for item in redundancy_list:
                    No_ids += item[1]
                self.redundancy = (No_ids/len(redundancy_list))
                if self.seq_coverage == 100:
                    score_range = list(range(score_level,8))
                    self.Dialog_insert("{0}{1}{2}{3:2.2f}{4}{5}".format("At score level ",score_level, " the sequence coverage is ",self.seq_coverage,"%", "\n" ))
                    if Use_seq_cutoff == 0:
                        score_level -= 1
                    else:
                        pass
                else:
                    self.Dialog_insert("{0}{1}{2}{3:2.2f}{4}{5}".format("At score level ",score_level, " the sequence coverage is ",self.seq_coverage,"%", "\n" ))
                    score_level -= 1
        if self.seq_coverage != 100:
            score_range = list(range(MinSeqScr,8))
        else:
            pass
        score_range.reverse()
        sorted_list = []
        seq_set = set()
        #Creates the list that used to gain information about the different RT's, IM's and number of times it was identified
        to_be_data_mined = []
        for scores in score_range:
            ids = score_list[scores]
            for item in ids:
                pre_csv = []
                NoId = 0
                while NoId < 63:
                    pre_csv.append(self.sorted_dict[item[0]][NoId][item[1]])
                    NoId += 1
                to_be_data_mined.append(pre_csv)
        self.data_mining_dict['Data mining'] = to_be_data_mined
        #Creates the masterlist to be used in the final CSV file
        for scores in score_range:
            ids = score_list[scores]
            for item in ids:
                seq = self.sorted_dict[item[0]][24][item[1]]
                if seq in seq_set:
                    pass
                else:
                    seq_set.add(seq)
                    sorted_list.append((item[0],item[1]))
        to_csv = [('protein.key','protein.Entry','protein.Accession','protein.Description','protein.dataBaseType','protein.score','protein.falsePositiveRate',
                   'protein.avgMass','protein.MatchedProducts','protein.matchedPeptides','protein.digestPeps','protein.seqCover(%)','protein.MatchedPeptideIntenSum',
                   'protein.top3MatchedPeptideIntenSum','protein.MatchedProductIntenSum','protein.fmolOnColumn','protein.ngramOnColumn','protein.Key_ForHomologs',
                   'protein.SumForTotalProteins','peptide.Rank','peptide.Pass','peptide.matchType','peptide.modification','peptide.mhp','peptide.seq',
                   'peptide.OriginatingSeq','peptide.seqStart','peptide.seqLength','peptide.pI','peptide.componentID','peptide.MatchedProducts',
                   'peptide.UniqueProducts','peptide.ConsectiveMatchedProducts','peptide.ComplementaryMatchedProducts','peptide.rawScore','peptide.score',
                   'peptide.(X)-P Bond','peptide.MatchedProductsSumInten','peptide.MatchedProductsTheoretical','peptide.MatchedProductsString','peptide.ModelRT',
                   'peptide.Volume','peptide.CSA','peptide.ModelDrift','peptide.RelIntensity','precursor.leID','precursor.mhp','precursor.mhpCal','precursor.retT',
                   'precursor.inten','precursor.calcInten','precursor.charge','precursor.z','precursor.mz','precursor.Mobility','precursor.MobilitySD',
                   'precursor.fwhm','precursor.liftOffRT','precursor.infUpRT','precursor.infDownRT','precursor.touchDownRT','prec.rmsFWHMDelta',
                   'peptidePrecursor.deltaMhpPPM')]
        for item in sorted_list:
            pre_csv = []
            NoId = 0
            while NoId < 63:
                pre_csv.append(self.sorted_dict[item[0]][NoId][item[1]])
                NoId += 1
            to_csv.append(pre_csv)
        self.master_dict['Master list'] = to_csv
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        self.Dialog_insert("Score_sorter {0}\n".format(difference))

    
    def Score_overview(self): ##Slow
        """
        Score_dict + Seq_dict -> .csv and .txt
        
        A .csv file is created that lists all of the identified sequences in the order of how well they scored. 
        They are furthermore sorted according to the sequence start in decending order and the length of the seqeunce in desending order.
        The output is a .txt file containing the overview and a .csv file that contains all the information needed to place the sequence in dynamx
        """
        Start_time = datetime.datetime.now()
        from operator import itemgetter
        from itertools import groupby
        score_7 = []
        score_6 = []
        score_5 = []
        score_4 = []
        score_3 = []
        score_2 = []
        score_1 = []
        score_0 = []
        list_of_keys = self.score_dict.keys()
        for key in list_of_keys:
            entry_score_list = self.score_dict[key]
            for item in entry_score_list:
                if item[1] == 7:
                    score_7.append((key,item[0]))
                elif item[1] == 6:
                    score_6.append((key,item[0]))
                elif item[1] == 5:
                    score_5.append((key,item[0]))
                elif item[1] == 4:
                    score_4.append((key,item[0]))
                elif item[1] == 3:
                    score_3.append((key,item[0]))
                elif item[1] == 2:
                    score_2.append((key,item[0]))
                elif item[1] == 1:
                    score_1.append((key,item[0]))
                elif item[1] == 0:
                    score_0.append((key,item[0]))
        score_list = [score_7 ,score_6, score_5, score_4, score_3, score_2, score_1, score_0]
        global directory
        directory = tk.filedialog.askdirectory()        
        score_overview_location = "{0}/{1}{2}".format(directory,Prot_ident,"_Score_overview.csv")              
        with open (score_overview_location, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            header_row = ["Sequence", "Sequence start", "Sequence length", "Modification", 
                          "MHP", "RT", "IM", "Charge State", "Intensity"]
            writer.writerow(header_row)
            score = 7
            for item in score_list:
                list_for_sorting = []
                for ite in item:
                    sequence = self.sorted_dict[ite[0]][24][ite[1]]
                    sequence_start = int(self.sorted_dict[ite[0]][26][ite[1]]) + 1
                    seq_length = int(self.sorted_dict[ite[0]][27][ite[1]]) + sequence_start
                    modifications = self.sorted_dict[ite[0]][22][ite[1]]
                    MHP = self.sorted_dict[ite[0]][46][ite[1]]
                    RT = self.sorted_dict[ite[0]][48][ite[1]]
                    IM = self.sorted_dict[ite[0]][54][ite[1]]
                    charge_state = self.sorted_dict[ite[0]][52][ite[1]]
                    Intensity = self.sorted_dict[ite[0]][49][ite[1]]
                    list_for_sorting.append([sequence, sequence_start, seq_length, modifications, MHP, RT, IM, charge_state, Intensity])
                list_for_sorting.sort(key=itemgetter(1))
                grouped = groupby(list_for_sorting, itemgetter(0))
                list_for_writing = []
                for elt, items in grouped:
                    for i in items:
                        list_for_writing.append(i)
                score_row = ["{0}: {1}".format("Score level",score)]            
                writer.writerow(score_row)
                for it in list_for_writing:
                    writer.writerow(it)
                score -= 1
        csvfile.close()
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        self.Dialog_insert("Score_overview {0}\n".format(difference))
        
    def Master_list_editor(self): ##RENAME, reflect a dataminer more than a masterlist creator
        """
        For all the peptides in the master list the number of times it made it past the sorting step and the number of times in total it 
        is identified is counted. Furthermore for all the identifications of a peptide that made it past the sorting all the RT, IM are futhermore identified
        This is packed into a dictionary together with the seq start and length. This dictionary is used in the RT determination and 
        in the helper report writer function
        """
        Start_time = datetime.datetime.now()
        master_seq_dict = {}
        key = 'Master list'
        master_entries = len(self.master_dict[key])
        master_entry_index = 1
        while master_entry_index < master_entries:
            sequence = self.master_dict[key][master_entry_index][24]
            seq_start = self.master_dict[key][master_entry_index][26]
            master_seq_dict[sequence] = seq_start
            master_entry_index += 1
        master_seqs = master_seq_dict.keys()
        for item in master_seqs:
            seq_values = []
            RT_list = []
            IM_list = []
            occurrence_count = 0
            file_entries = len(self.data_mining_dict['Data mining'])
            file_entry = 1
            while file_entry < file_entries:
                match_seq = self.data_mining_dict['Data mining'][file_entry][24]
                if match_seq == item:
                    RT = self.data_mining_dict['Data mining'][file_entry][48]                   
                    RT_list.append(RT)
                    IM = self.data_mining_dict['Data mining'][file_entry][54]
                    Charge = self.data_mining_dict['Data mining'][file_entry][52]
                    IM_list.append([Charge, IM])
                    occurrence_count += 1
                    file_entry += 1
                else:
                    file_entry += 1
            seq_start = int(master_seq_dict[item])
            seq_length = len(item)
            seq_values.append(seq_start)
            seq_values.append(seq_length)
            seq_values.append(RT_list)
            seq_values.append(IM_list)
            seq_values.append(occurrence_count)
            self.edited_master_seq_dict[item] =  seq_values
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        self.Dialog_insert("Master_list_editor {0}\n".format(difference))            
    
    def RT_User_SD_guiding_determination(self):
        """
        For the peptides that made it past the sorting,the standard deviation is calucaleted for all the RT values
        assigned to a sequence. If the SD is larger than a user determined value the user is promted with the multilistbox treeview window
        were the user can decide which RT value should be used 
        """
        Start_time = datetime.datetime.now()
        global pre_selection_list
        Seqs = self.edited_master_seq_dict.keys()
        Seq_and_RT = {}
        for item in Seqs:
            RT_list = self.edited_master_seq_dict[item][2]
            RT_sum = 0
            No_RT_values = 0            
            for itemRT in RT_list:
                RT_sum += itemRT
                No_RT_values += 1
            Average = RT_sum/No_RT_values
            spread_sum = 0
            for itemRT in RT_list:
                RT = itemRT
                spread = (RT-Average)**2
                spread_sum += spread
            SD = spread_sum**1/2
            if SD < Allowed_SD:
                RT = Average
                Seq_and_RT[item] = RT
            else:
                pre_selection_list = []
                entry_list = self.data_mining_dict['Data mining']
                entry_index = 0
                for entry in entry_list:
                    seq = entry[24]
                    value = []
                    if seq == item: 
                        id_index = 0
                        while id_index < 63:
                            if id_index == 30: #Number of products
                                Num_prod = entry[id_index]
                                id_index += 1
                            #elif id_index == 32: #Number of consecutive products
                            #    value.append(entry[id_index])
                            #    id_index += 1                                
                            #elif id_index == 34: #Random ID_ The PPA is calculated here
                            #    seq_len = int(entry[27])
                            #    No_prod = int(entry[30])
                            #    if No_prod == 0:
                            #        No_prod_per_AA = "{0:.2f}".format(seq_len)
                            #    else:
                            #        No_prod_per_AA = "{0:.2f}".format(No_prod/seq_len)
                            #    value.append(No_prod_per_AA)
                            #    id_index += 1
                            #elif id_index == 35: #Peptide score
                            #    value.append(entry[id_index])
                            #    id_index += 1
                            #elif id_index == 37: #The int sum of the products
                            #    value.append(entry[id_index])
                            #    id_index += 1
                            elif id_index == 48: #The RT value
                                retention_time = entry[id_index]
                                id_index += 1
                            elif id_index == 49: #Precursor intensity
                                precursor_int = entry[id_index]
                                id_index += 1
                            elif id_index == 52: #The charge state for which the precursor information is recorded
                                z = entry[id_index]
                                id_index += 1
                            elif id_index == 54: #The precursor IM value
                                precursor_im = entry[id_index]
                                id_index += 1
                            elif id_index == 62: #Mass delta
                                delta_mass = entry[id_index]
                                id_index += 1
                            else:
                                id_index += 1
                        pre_selection_list.append((item, Num_prod, precursor_int, retention_time, precursor_im, z, delta_mass))
                    else:
                        pass
                    entry_index += 1
                self.RT_Selection_popup()
                Seq_and_RT[item] = RT
        #This section of the function changes the RT value for the seqeunces in the edited master list dictionary
        to_master_list =[]
        No_entries = len(self.master_dict['Master list'])
        entry_index = 0
        while entry_index < No_entries:
            id_index = 0
            if entry_index == 0:
                to_master_list.append(self.master_dict['Master list'][0])
                entry_index += 1
            elif entry_index > 0:
                entry_value = []
                seq = self.master_dict['Master list'][entry_index][24]
                while id_index < 63:
                    if id_index == 48:
                        RT = Seq_and_RT[seq]
                        RT_str = "{0:.4f}".format(RT)
                        id_index += 1
                        entry_value.append(RT_str)
                    else:
                        value = self.master_dict['Master list'][entry_index][id_index]
                        entry_value.append(value)
                        id_index += 1
                to_master_list.append(entry_value)
                entry_index += 1
        self.final_edit['Master list'] = to_master_list 
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        self.Dialog_insert("RT_User_SD_guiding_determination {0}\n".format(difference))        
        
    def The_CSV_Writer(self):
        """
        Master list dict formatted to look like a PLGS file ---> .csv file
        
        First the entries in the Master dict is sorted according to the match type value:
        PepFrag1
        PepFrag2
        VarMod
        Insource
        NeutralLoss_H2O
        NeutralLoss_NH3
        
        Secondly these PLGS parameters are calculated and assigned in the file:
        
        This makes the written .csv file look like the PLGS output
        
        ##Both the insource and neutralloss can be removed 
        
        """
        Start_time = datetime.datetime.now()
        import csv 
        number_of_entries = len(self.final_edit['Master list'])
        key = 'Clean_master_list'
        entry_index = 0
        to_master_list = []
        sorted_dict = {}
        PepFrag1 = []
        PepFrag2 = []
        VarMod = []
        InSource = []
        NeutralLoss_H2O = []
        NeutralLoss_NH3 = []
        ######## This section sorts the peptide according to the match type value
        while entry_index < number_of_entries:
            if entry_index == 0:
                PepFrag1.append(self.final_edit['Master list'][0])
                entry_index += 1
            else:
                id_index = 21
                value = self.final_edit['Master list'][entry_index][id_index]
                value2 = self.final_edit['Master list'][entry_index]
                if value == 'PepFrag1':
                    PepFrag1.append(value2)
                elif value == 'PepFrag2':
                    PepFrag2.append(value2)
                elif value == 'VarMod':
                    VarMod.append(value2)
                elif value == 'InSource':
                    InSource.append(value2)
                elif value == 'NeutralLoss_H2O':
                    NeutralLoss_H2O.append(value2)
                elif value == 'NeutralLoss_NH3':
                    NeutralLoss_NH3.append(value2)
                entry_index += 1
        for item in PepFrag2:
            PepFrag1.append(item)
        for item in VarMod:
            PepFrag1.append(item)    
        for item in InSource:
            PepFrag1.append(item)
        for item in NeutralLoss_H2O:
            PepFrag1.append(item)
        for item in NeutralLoss_NH3:
            PepFrag1.append(item)
        sorted_dict['Master list'] = PepFrag1
        ########
        #The Following sections modifies the master dict so the final .csv file matches the format of the PLGS .csv files
        entry_index = 0
        entry_index2 = 1
        while entry_index < number_of_entries:
            id_index = 0
            if entry_index == 0: # Adds the header values (column identifiers)
                to_master_list.append(self.master_dict['Master list'][0])
                entry_index += 1
            elif entry_index == 1:
                entry_value = []
                while id_index < 63:
                    if id_index == 5:
                        score = "{0:.4f}".format(float(sorted_dict['Master list'][1][5]))
                        id_index += 1
                        entry_value.append(score)
                    if id_index == 7:
                        value = "{0:.4f}".format(float(sorted_dict['Master list'][1][7]))
                        id_index += 1
                        entry_value.append(value)
                    if id_index == 8:
                        Pep_match_prodc = 0
                        while entry_index2 < number_of_entries:
                            Pep_match_prodc += int(sorted_dict['Master list'][entry_index2][30])
                            entry_index2 += 1
                        entry_index2 = 1
                        id_index += 1
                        Pep_match_prodc = "{0}".format(Pep_match_prodc)
                        entry_value.append(Pep_match_prodc)
                    if id_index == 9:
                        PepFrag1 = 0
                        PepFrag2 = 0
                        VarMod = 0
                        while entry_index2 < number_of_entries:
                            value = sorted_dict['Master list'][entry_index2][21] 
                            if value == 'PepFrag1':
                                PepFrag1 += 1
                                entry_index2 += 1
                            elif value == 'PepFrag2':
                                PepFrag2 += 1
                                entry_index2 += 1
                            elif value == 'VarMod':
                                VarMod += 1
                                entry_index2 += 1
                            else:
                                entry_index2 += 1
                        entry_index2 = 1
                        matched_peptides = "{0}".format(PepFrag1 + PepFrag2 + VarMod)
                        id_index += 1
                        entry_value.append(matched_peptides)
                    if id_index == 10:
                       digested_peptides = sorted_dict['Master list'][1][10]
                       id_index += 1
                       entry_value.append(digested_peptides)
                    if id_index == 11:
                        SeqCover = "{0:.2f}".format(float(sorted_dict['Master list'][1][11]))
                        id_index += 1
                        entry_value.append(SeqCover)
                    if id_index == 12:
                       Matchedpepintsum = 0
                       while entry_index2 < number_of_entries:
                           Matchedpepintsum += int(sorted_dict['Master list'][entry_index2][49])
                           entry_index2 += 1
                       Matchedpepintsum = "{0}".format(Matchedpepintsum)
                       entry_index2 = 1
                       id_index += 1 
                       entry_value.append(Matchedpepintsum)
                    if id_index == 13:
                        top3MatchedPepIntSum_list = []
                        while entry_index2 < number_of_entries:
                           top3MatchedPepIntSum_list.append(int(sorted_dict['Master list'][entry_index2][49]))
                           entry_index2 += 1
                        top3MatchedPepIntSum_list.sort(reverse = True)
                        top3matchedpepsum = "{0}".format(top3MatchedPepIntSum_list[0] + top3MatchedPepIntSum_list[1] + top3MatchedPepIntSum_list[2])
                        entry_index2 = 1
                        id_index += 1
                        entry_value.append(top3matchedpepsum)
                    if id_index == 14:
                        matchedproductionsum = 0
                        while entry_index2 < number_of_entries:
                            matchedproductionsum += int(sorted_dict['Master list'][entry_index2][37])
                            entry_index2 += 1
                        entry_index2 = 1
                        id_index += 1
                        matchedproductionsum = "{0}".format(matchedproductionsum)
                        entry_value.append(matchedproductionsum)
                    if id_index == 18:
                        Sumforprotein = 1
                        id_index += 1
                        entry_value.append(Sumforprotein)
                    if id_index == 19:
                        peprank = 1
                        id_index += 1
                        entry_value.append(peprank)
                        peprank +=1
                    if id_index == 30:
                        value = str(sorted_dict['Master list'][1][30])
                        id_index += 1
                        entry_value.append(value)
                    if id_index == 49:
                        value = str(sorted_dict['Master list'][1][49])
                        id_index += 1
                        entry_value.append(value)
                    if id_index == 62:
                        value = "{0:.4f}".format(sorted_dict['Master list'][1][62])
                        id_index += 1
                        entry_value.append(value)
                    else:
                        value = sorted_dict['Master list'][1][id_index]
                        id_index += 1
                        entry_value.append(value)
                to_master_list.append(entry_value)
                entry_index += 1
            elif entry_index > 1:
                entry_value = []
                while id_index < 63:
                    if id_index == 5:
                       id_index += 1
                       entry_value.append(score)
                    if id_index == 7:
                        value = "{0:.4f}".format(float(sorted_dict['Master list'][entry_index][7]))
                        id_index += 1
                        entry_value.append(value)
                    if id_index == 8:
                        id_index += 1
                        entry_value.append(Pep_match_prodc)
                    if id_index == 9:
                        id_index += 1
                        entry_value.append(matched_peptides)
                    if id_index == 10:
                       id_index += 1
                       entry_value.append(digested_peptides)
                    if id_index == 11:
                        id_index += 1
                        entry_value.append(SeqCover)
                    if id_index == 12:
                       id_index += 1
                       entry_value.append(Matchedpepintsum)
                    if id_index == 13:
                        id_index += 1
                        entry_value.append(top3matchedpepsum)
                    if id_index == 14:
                       id_index += 1
                       entry_value.append(matchedproductionsum)
                    if id_index == 18:
                        Sumforprotein = 0
                        id_index += 1
                        entry_value.append(Sumforprotein)
                    if id_index == 19:
                        id_index += 1
                        entry_value.append(peprank)
                        peprank +=1
                    if id_index == 30:
                        value = str(sorted_dict['Master list'][entry_index][30])
                        id_index += 1
                        entry_value.append(value)
                    if id_index == 49:
                        value = str(sorted_dict['Master list'][entry_index][49])
                        id_index += 1
                        entry_value.append(value)
                    if id_index == 62:
                        value = "{0:.4f}".format(sorted_dict['Master list'][entry_index][62])
                        id_index += 1
                        entry_value.append(value)
                    else:
                        value = sorted_dict['Master list'][entry_index][id_index]
                        id_index += 1
                        entry_value.append(value)
                to_master_list.append(entry_value)
                entry_index += 1
        self.clean_dict[key] = to_master_list
        list_of_keys = self.clean_dict.keys()
        csv_filelocation = "{0}/{1}{2}".format(directory,Prot_ident,"_IA_final_peptide.csv")
        with open (csv_filelocation, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            for key in list_of_keys:
                entrie_index = 0
                entries = len(self.clean_dict[key])
                while entrie_index < entries:
                    row = self.clean_dict[key][entrie_index]
                    writer.writerow(row)
                    entrie_index += 1
        csvfile.close()
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        self.Dialog_insert("The_CSV_Writer {0}\n".format(difference)) 
    
    def Helper_Writer(self):
        """
        information --> txt file with the information
        
        All the gathered information is written into a txt file that can be used as an helper file
        including :
        Identified RT values
        Identified IM values
        How many times a peptide has been identified meeting the selection criteria
        How many times a peptide has been identified disreagarding the selection criteria
        To further the function of the helper report the sequence start values is added with 1 to mimic the dynamx notation
        
        """
        Start_time = datetime.datetime.now()
        from operator import itemgetter
        from itertools import groupby    
        list_of_keys = self.edited_master_seq_dict.keys()
        list_for_sorting = []
        for key in list_of_keys: 
            seq_and_key = []        
            seq = key
            seq_value = self.edited_master_seq_dict[key]
            seq_and_key.append(seq)
            seq_and_key.append(seq_value)
            list_for_sorting.append(seq_and_key)
        list_for_sorting.sort(key=itemgetter(1))
        grouped = groupby(list_for_sorting, itemgetter(0))
        list_for_writing = []
        for elt, items in grouped:
            for i in items:
                list_for_writing.append(i)
        seq_length_list = []
        RT_length_list = []
        IM_length_list = []
        for item in list_for_writing:
            seq = item[0]
            seq_length = len(seq)
            seq_length_list.append(seq_length)
            sequence_row_length = max(seq_length_list)
            RT = item[1][2]
            RT_length = len(RT)
            RT_length_list.append(RT_length)
            RT_row_length = max(RT_length_list)
            IM = item[1][3]
            IM_length = len(IM)
            IM_length_list.append(IM_length)
            IM_row_length = max(IM_length_list)
        RT_row_length_1 = RT_row_length * 7
        IM_row_length_1 = IM_row_length * 13
        helper_filelocation = "{0}/{1}{2}".format(directory,Prot_ident,"_Helper.txt")
        file = open(helper_filelocation, 'w')
        ID = '{0:<{width}}'.format('Sequence', width=sequence_row_length)
        ID2 = repr('seq_start').rjust(10)
        ID3 = repr('RT').rjust(RT_row_length_1-3)
        ID4 = repr('Charge state and IM').rjust(IM_row_length_1)
        ID5 = repr('Occurencies').rjust(10)
        header_final = ID + ID2 + ID3 + ID4 + '   ' + ID5 + '\n'
        sequence_coverage_string = "The sequence coverage is {0:2.2f}".format(self.seq_coverage) + "%" + "\n" 
        number_of_peptides = "The number of identified peptides is {0}".format(len(self.edited_master_seq_dict)) + "\n"
        redundancy = "The redundancy is {0}\n".format(self.redundancy)
        file.write(sequence_coverage_string)
        file.write(number_of_peptides)
        file.write(redundancy)
        file.write(header_final)
        string_list = []
        for item in list_for_writing:
            RT_string = ''
            IM_string = ''
            sequence = item[0]
            seq_start = int(item[1][0]) + 1
            RT = item[1][2]
            for i in RT:
                if i != None:
                    RT_i = '{0:.2f}'.format(float(i))
                    RT_string += RT_i + ', '
                else:
                    pass
            IM = item[1][3]
            for it in IM:
                if it != None:
                    IM_it = '{0:.2f}'.format(float(it[1]))
                    charge_state = '{0}'.format(it[0])
                    IM_string += charge_state+ ', ' + IM_it + ', '
                else:
                    pass
            count = item[1][4]
            string = '{0:<{width}}'.format(sequence, width=sequence_row_length) 
            string2 = repr(seq_start).rjust(10)
            string3 = repr(RT_string).rjust(RT_row_length_1)
            string4 = repr(IM_string).rjust(IM_row_length_1)
            string5 = repr(count).rjust(10)
            string_final = string + string2 + string3 + string4 + string5 + '\n'
            file.write(string_final)
            string_list.append(string_final)
        file.close()
        End_time = datetime.datetime.now()
        difference =  (End_time - Start_time).total_seconds()
        self.Dialog_insert("Helper_Writer {0}\n".format(difference))


# This section starts and adjusts the GUI window to the determined settings
root=tk.Tk()
root.wm_title("LARS, Listing of Analytically Relevant Sequences")
Application(root).pack(side="top", fill="both", expand=True)
root.mainloop()
