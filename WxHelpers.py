from typing import Optional
import time
import wx
from wx import _core

from Log import Log


# This is used:
#   with ModalDialogManager(dialog object, object's init arguments...) as dlg
#       dlg.ShowModal()
#       etc.
#   It deals with dlg.destroy()

class ModalDialogManager():
    def __init__(self, classType: callable, *args, **kargs):
        self._class: callable=classType
        self._args=args
        self._kargs=kargs

    def __enter__(self):
        self._dlg=self._class(*self._args, **self._kargs)
        return self._dlg

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._dlg.Destroy()


# Usage: with ModalDialogManager(ProgressMessage2, message) as pm:
class ProgressMessage2(object):
    def __init__(self, *args, **kargs):
        self._pm=ProgressMessage(args)
        self._args=args[1:]
        self._kargs=kargs
        if "parent" in kargs:
            self._pm._parent=kargs["parent"]
            del kargs["parent"]
        self._pm.Show(*args, **self._kargs)


    def __enter__(self):
        # self, s: str|None, close: bool=False, delay: float=0)
        assert False


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._pm.Close()


    def Update(self, message: str|None, delay: float=0):
        self._pm.Show(message)
        if delay > 0:
            time.sleep(delay)


    def Destroy(self):
        self._pm.Close()


#==============================================================
# A class to display progress messages
#       ProgressMessage(parent).Show(message)       # Display a message, creating a popup dialog if needed
#       ProgressMessage(parent).Close(delay=sec)    # Delay sec seconds and then close the progress message
# It may also be used as:
#   with ProgressMsg(parent, "message", delay=1 as msg:
#       ...
#       ...
#       etc.
class ProgressMessage(object):
    _progressMessageDlg: wx.ProgressDialog=None

    def __init__(self, parent: Optional[wx.TopLevelWindow]=None) -> None:
        self._parent=parent

    def Show(self, s: str|None, close: bool=False, delay: float=0) -> None:  # ConInstanceFramePage
        if ProgressMessage._progressMessageDlg is None:
            ProgressMessage._progressMessageDlg=wx.ProgressDialog("progress", s, maximum=100, parent=None, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        Log(f"ProgressMessage.Show('{s}')")
        self._progressMessageDlg.Pulse(s)

        if close:
            self.Close(delay)

    def Destroy(self):
        self.Close()

    def UpdateMessage(self, s: str):
        if ProgressMessage._progressMessageDlg is None:
            Log("ProgressMessage.UpdateMessage() called without an existing ProgressDialog")
            return
        Log("ProgressMessage.Update('"+s+"')")
        ProgressMessage._progressMessageDlg.Update(0, s)
        ProgressMessage._progressMessageDlg.Pulse(s)


    def Close(self, delay: float=0) -> None:
        if ProgressMessage._progressMessageDlg is None:
            Log("ProgressMessage.Close() called without an existing ProgressDialo")
            return

        if delay > 0:
            time.sleep(delay)
        ProgressMessage._progressMessageDlg.WasCancelled()
        ProgressMessage._progressMessageDlg=None
        if self._parent is not None:
            self._parent.SetFocus()
            self._parent.Raise()

# class ProgressMsg(object):
#     def __init__(self, parent: wx.TopLevelWindow | None, message: str, delay: float= 0.5) -> None:
#         self.pm=ProgressMessage(parent)
#         self._parent=parent
#         self.message=message
#         self.delay=delay
#
#     def __enter__(self):
#         self.pm.Show(self.message, delay=self.delay)
#         # If a parent has been defined, move the progress message to the parent's position
#         # This is handy when there's multiple monitors
#         if self._parent is not None:
#             self.pm._progressMessageDlg.SetPosition(self._parent.GetPosition())
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.pm.Close()


# Returns True if processing should continue; False if it should end
def OnCloseHandling(event, needssaving: bool, msg: str) -> bool:
    if needssaving:
        if event is None or type(event) == wx._core.CommandEvent:  # When the close event is None or is an ESC or the ID_Cancel button, it's not a veto-able event, so it needs to be handled separately
            resp=wx.MessageBox(msg, 'Warning', wx.OK|wx.CANCEL|wx.ICON_WARNING)
            if resp == wx.CANCEL:
                return True
        elif event.CanVeto():
            resp=wx.MessageBox(msg, 'Warning', wx.OK|wx.CANCEL|wx.ICON_WARNING)
            if resp == wx.CANCEL:
                event.Veto()
                return True

    return False


# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class QueryDialog
###########################################################################

class QueryDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		lable = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, wx.EmptyString ), wx.VERTICAL )

		self.wxLable = wx.StaticText( lable.GetStaticBox(), wx.ID_ANY, u"Enter the new column's name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.wxLable.Wrap( -1 )

		lable.Add( self.wxLable, 0, wx.ALL, 5 )

		self.m_textctl = wx.TextCtrl( lable.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_textctl.SetMinSize( wx.Size( 200,-1 ) )

		lable.Add( self.m_textctl, 0, wx.ALL, 5 )

		fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_buttonOK = wx.Button( lable.GetStaticBox(), wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_buttonOK.SetDefault()
		fgSizer4.Add( self.m_buttonOK, 0, wx.ALL, 5 )

		self.m_buttonCancel = wx.Button( lable.GetStaticBox(), wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_buttonCancel, 0, wx.ALL, 5 )


		lable.Add( fgSizer4, 1, wx.EXPAND, 5 )


		self.SetSizer( lable )
		self.Layout()
		lable.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_buttonOK.Bind( wx.EVT_BUTTON, self.OnOk )
		self.m_buttonCancel.Bind( wx.EVT_BUTTON, self.OnCancel )

	def __del__( self ):
		pass

	# Virtual event handlers, overide them in your derived class
	def OnOk( self, event ):
		self.EndModal(wx.ID_OK)

	def OnCancel( self, event ):
		self.EndModal(wx.ID_CANCEL)


def MessageBoxInput(s: str="", title="", initialValue: str="", ignoredebugger=True) -> str:
    dlg=QueryDialog(None)
    dlg.Title=title
    dlg.wxLable.LabelText=s

    dlg.m_textctl.Value=initialValue
    ret=""
    try:
        if dlg.ShowModal() == wx.ID_OK:
            ret=dlg.m_textctl.Value
    finally:
        dlg.Destroy()
    return ret


def MessageBoxInpu2(prompt: str = "", title="", initialValue: str = "", ignoredebugger=True) -> str:
    dlg=QueryDialog(None)
    dlg.Title=title
    dlg.wxLable.SetLabelText(prompt)

    dlg.m_textctl =initialValue
    ret=""
    try:
        if dlg.ShowModal() == wx.ID_OK:
            ret=dlg.m_textctl.Value
    finally:
        dlg.Destroy()
    return ret


#------------------------------------------------------------------------
# This one usefully resizes to display the whole title
def wxMessageDialogInput(prompt: str="", title: str="", parent=None, initialValue: str="", ignoredebugger=True) -> str:
    dlg=wx.TextEntryDialog(parent, prompt, caption=title, value=initialValue)
    ret=""
    if dlg.ShowModal() == wx.ID_OK:
        ret=dlg.GetValue()
    dlg.Destroy()
    return ret


#------------------------------------------------------------------------
# Add a character to the end of a wxPython text box
def AddChar(text: str, code) -> str:
    if code == wx.WXK_BACK and len(text) > 0:
        return text[:-1]
    if code < 32 or code > 126:
        return text
    return text+chr(code)


#------------------------------------------------------------------------
# Process a new character entered into a wxPython text box
def ProcessChar(text: str, code: int, cursorloc: int) -> (str, int):
    match code:
        case wx.WXK_BACK:
            if cursorloc > 0:
                text=text[:cursorloc-1]+text[cursorloc:]
                cursorloc=cursorloc-1
        case wx.WXK_DELETE:
            if cursorloc < len(text):
                text=text[:cursorloc]+text[cursorloc+1:]
        case wx.WXK_LEFT:
            if cursorloc > 0:
                cursorloc=cursorloc-1
        case wx.WXK_RIGHT:
            if cursorloc < len(text):
                cursorloc+=1
        case wx.WXK_END:
            cursorloc=len(text)
        case wx.WXK_HOME:
            cursorloc=0
        case x if x >= 32 and x <= 126:
            text=text[:cursorloc]+chr(code)+text[cursorloc:]
            cursorloc+=1

    return text, cursorloc