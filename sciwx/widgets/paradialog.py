import wx, platform
from .normal import *
from .histpanel import HistPanel

widgets = { 'ctrl':None, 'slide':FloatSlider, int:NumCtrl, 'path':PathCtrl,
            float:NumCtrl, 'lab':Label, bool:Check, str:TextCtrl, list:Choice,
            'color':ColorCtrl, 'any':AnyType, 'chos':Choices, 'hist':HistPanel}

def add_widget(key, value): widgets[key] = value

class ParaDialog (wx.Dialog):
    def __init__( self, parent, title):
        wx.Dialog.__init__ (self, parent, -1, title, style = wx.DEFAULT_DIALOG_STYLE)
        self.lst = wx.BoxSizer( wx.VERTICAL )
        self.tus = []
        self.on_ok = self.on_cancel = self.on_help = None
        self.handle = print
        self.ctrl_dic = {}
        boxBack = wx.BoxSizer()
        boxBack.Add(self.lst, 0, wx.ALL, 10)
        self.SetSizer( boxBack )
        self.Layout()

    def commit(self, state):
        self.Destroy()
        if state=='ok' and self.on_ok:self.on_ok()
        if state=='cancel' and self.on_cancel:self.on_cancel()

    def add_confirm(self, modal=True):
        sizer = wx.BoxSizer( wx.HORIZONTAL )
        self.btn_ok = wx.Button( self, wx.ID_OK, 'OK', wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        sizer.Add( self.btn_ok, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.btn_cancel = wx.Button( self, wx.ID_CANCEL, 'Cancel', wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        sizer.Add( self.btn_cancel, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.btn_help = wx.Button( self, wx.ID_HELP, 'Help', wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        sizer.Add( self.btn_help, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
        self.lst.Add(sizer, 0, wx.ALIGN_RIGHT, 5 )
        self.btn_help.Bind(wx.EVT_BUTTON, lambda e: self.on_help and self.on_help())
        if not modal:
            self.btn_ok.Bind( wx.EVT_BUTTON, lambda e:self.commit('ok'))
            self.btn_cancel.Bind( wx.EVT_BUTTON, lambda e:self.commit('cancel'))
            
        #self.lst.Add()

    def init_view(self, items, para, preview=False, modal = True):
        self.para = para
        for item in items:
            self.add_ctrl_(widgets[item[0]], item[1], item[2:])
        if preview:self.add_ctrl_(Check, 'preview', ('preview',))
        self.reset(para)
        self.add_confirm(modal)
        self.pack()
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        print('bind close')
    
    
    def OnDestroy( self, event ):
        self.set_handle(None)
        self.on_cancel = self.on_ok = self.on_help = None
        del self.ctrl_dic

    def parse(self, para) :
        self.add_ctrl_(widgets[para[0]], *para[1:])

    def add_ctrl_(self, Ctrl, key, p):
        ctrl = Ctrl(self, *p)
        if not p[0] is None: 
            self.ctrl_dic[key] = ctrl
        if hasattr(ctrl, 'Bind'):
            ctrl.Bind(None, self.para_changed)
        pre = ctrl.prefix if hasattr(ctrl, 'prefix') else None
        post = ctrl.postfix if hasattr(ctrl, 'postfix') else None
        self.tus.append((pre, post))
        self.lst.Add( ctrl, 0, wx.EXPAND, 0 )

    def pack(self):
        self.Layout()
        mint, minu = [], []
        for t,u in self.tus:
            if not t is None: mint.append(t.GetSize()[0])
            if not u is None:minu.append(u.GetSize()[0])
        for t,u in self.tus:
            if not t is None:t.SetInitialSize((max(mint),-1))
            if not u is None:u.SetInitialSize((max(minu),-1))
        self.Fit()

    def para_check(self, para, key):pass

    def para_changed(self, obj):
        key = ''
        para = self.para
        for p in self.ctrl_dic:
            if p in para:
                para[p] = self.ctrl_dic[p].GetValue()
            if self.ctrl_dic[p] == obj: key = p

        sta = sum([i is None for i in list(para.values())])==0
        self.btn_ok.Enable(sta)
        if not sta: return
        self.para_check(para, key)
        if 'preview' not in self.ctrl_dic:return
        if not self.ctrl_dic['preview'].GetValue():
            if key=='preview' and self.on_cancel != None: 
                return self.on_cancel()
            else: return
        self.handle(para)

    def reset(self, para=None):
        if para!=None:self.para = para
        for p in list(self.para.keys()):
            if p in self.ctrl_dic:
                self.ctrl_dic[p].SetValue(self.para[p])

    def get_para(self): return self.para

    def set_handle(self, handle=None):
        self.handle = handle if not handle is None else print

    def __del__( self ):
        print('panel config deleted!')

def get_para(para, view, title='Parameter', parent=None):
    pd = ParaDialog(parent, title)
    pd.init_view(view, para)
    pd.pack()
    rst = pd.ShowModal()
    pd.Destroy()
    return rst == 5100

if __name__ == '__main__':
    para = {'name':'yxdragon', 'age':10, 'h':1.72, 'w':70, 'sport':True, 'sys':'Mac', 'lan':['C/C++', 'Python'], 'c':(255,0,0)} 

    view = [('lab', 'lab', 'This is a questionnaire'),
            (str, 'name', 'name', 'please'), 
            (int, 'age', (0,150), 0, 'age', 'years old'),
            (float, 'h', (0.3, 2.5), 2, 'height', 'm'),
            ('slide', 'w', (1, 150), 0, 'weight','kg'),
            (bool, 'sport', 'do you like sport'),
            (list, 'sys', ['Windows','Mac','Linux'], str, 'favourite', 'system'),
            ('chos', 'lan', ['C/C++','Java','Python'], 'lanuage you like(multi)'),
            ('color', 'c', 'which', 'you like')]

    app = wx.App()
    pd = ParaDialog(None, 'Test')
    pd.init_view(view, para, preview=True, modal=False)
    pd.pack()
    pd.ShowModal()
    print(para)
    app.MainLoop()
