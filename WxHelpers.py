from typing import Union, Tuple, Optional, List
import time
import wx
from wx import _core

from Log import Log, LogClose


# This is used:
#   with ModalDialogManager(dialog object, object's init arguments...) as dlg
#       dlg.ShowModal()
#       etc.
#   It deals with dlg.destroy()

class ModalDialogManager():
    def __init__(self, name: wx.Dialog, *args, **kargs):
        self._name: wx.Dialog=name
        self._args=args
        self._kargs=kargs

    def __enter__(self):
        self._dlg=self._name(*self._args, **self._kargs)
        return self._dlg

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._dlg.Destroy()


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

    def __init__(self, parent: Optional[wx.TopLevelWindow]) -> None:
        self._parent=parent

    def Show(self, s: Optional[str], close: bool=False, delay: float=0) -> None:  # ConInstanceFramePage
        if ProgressMessage._progressMessageDlg is None:
            ProgressMessage._progressMessageDlg=wx.ProgressDialog("progress", s, maximum=100, parent=None, style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        Log("ProgressMessage.Show('"+s+"')")
        ProgressMessage._progressMessageDlg.Pulse(s)

        if close:
            self.Close(delay)

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

class ProgressMsg(object):
    def __init__(self, parent: Optional[wx.TopLevelWindow], message: str, delay: float= 0.5) -> None:
        self.pm=ProgressMessage(parent)
        self._parent=parent
        self.message=message
        self.delay=delay

    def __enter__(self):
        self.pm.Show(self.message, delay=self.delay)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pm.Close()


#
# Returns True if processing should continue; False if it should end
def OnCloseHandling(event, needssaving: bool, msg: str) -> bool:
    if needssaving:
        if event is None or type(event) == wx._core.CommandEvent:  # When the close event is None or is an ESC or the ID_Cancel button, it's not a vetoable event, so it needs to be handled separately
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
## Python code generated with wxFormBuilder (version Oct 26 2018)
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

		self.label = wx.StaticText( lable.GetStaticBox(), wx.ID_ANY, u"Enter the new column's name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label.Wrap( -1 )

		lable.Add( self.label, 0, wx.ALL, 5 )

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
		event.Skip()

	def OnCancel( self, event ):
		event.Skip()





def MessageBoxInput(s: str, title="", ignoredebugger=True) -> str:
    with QueryDialog(None) as dlg:
        dlg.Title=title
        if dlg.ShowModal() != wx.ID_OK:
            return ""
        return dlg.m_textctl.Value


#------------------------------------------------------------------------
# Add a character to a wxPython text box
def AddChar(text: str, code) -> str:
    if code == wx.WXK_BACK and len(text) > 0:
        return text[:-1]
    if code < 32 or code > 126:
        return text
    return text+chr(code)