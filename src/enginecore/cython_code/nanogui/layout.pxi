from libcpp.vector cimport vector


cdef class Layout:
    cdef nanogui.Layout* ptr
    pass

cdef class BoxLayout(Layout):
    #cdef nanogui.BoxLayout* ptr
    def __init__(self, int orientation, int alignment = <int> nanogui.Middle,
                 int margin = 0, int spacing = 0):
        self.ptr = new nanogui.BoxLayout(<nanogui.Orientation>orientation, <nanogui.Alignment>alignment,
                                         margin, spacing)
cdef class GroupLayout(Layout):
    #cdef nanogui.BoxLayout* ptr
    def __init__(self, int margin=15, int spacing=6, int groupSpacing=14, int groupIndent=20):
        self.ptr = new nanogui.GroupLayout(margin, spacing, groupSpacing, groupIndent)

cdef class AdvancedGridLayout(Layout):
    cdef nanogui.AdvancedGridLayout* advanced_ptr

    def __init__(self, list cols=None, list rows=None, int margin=0, set_helper_stuff=True):
        cdef vector[int] cols_ = cols if cols else []
        cdef vector[int] rows_ = rows if rows else []
        self.advanced_ptr = new nanogui.AdvancedGridLayout(cols_, rows_, margin)
        self.ptr = self.advanced_ptr

        if set_helper_stuff:
            self.advanced_ptr.setMargin(10)
            self.advanced_ptr.setColStretch(2, 1)

    # note: have not written an init because i'm lazy and dont need this other than to wrap it internally
    def set_anchor(self, Widget widget, Anchor anchor):
        self.advanced_ptr.setAnchor(widget.widget, anchor.ptr)

    @property
    def row_count(self):
        return self.advanced_ptr.rowCount()

    cpdef append_row(self, int size=0, float stretch=0.0):
        self.advanced_ptr.appendRow(size, stretch)

cdef class Anchor:
    cdef nanogui.Anchor ptr
    def __init__(self, int x, int y, w=None, h=None,
                 int horiz=<int> nanogui.Fill, int vert=<int> nanogui.Fill):
        if w is not None and h is not None:
            self.ptr = nanogui.Anchor(x, y, w, h, <nanogui.Alignment>horiz, <nanogui.Alignment>vert)
        else:
            self.ptr = nanogui.Anchor(x, y, <nanogui.Alignment>horiz, <nanogui.Alignment>vert)
