from libcpp.vector cimport vector


cdef class Layout:
    """
    A layout tells the GUI renderer how to lay out a widget
    eg, it may have 4 children, and a GroupLayout would put them in stack, but a BoxLayout might put them in a row
    and if you wanted them in a 2x2 grid, you'd use an AdvancedGridLayout
    """
    cdef nanogui.Layout* ptr

cdef class BoxLayout(Layout):
    """to quote the nanogui docs:
    Simple horizontal/vertical box layout.

    This widget stacks up a bunch of widgets horizontally or vertically.
    It adds margins around the entire container and a custom spacing between adjacent widgets.
    """
    def __init__(self, int orientation, int alignment = <int> nanogui.Middle,
                 int margin = 0, int spacing = 0):
        self.ptr = new nanogui.BoxLayout(<nanogui.Orientation>orientation, <nanogui.Alignment>alignment,
                                         margin, spacing)
cdef class GroupLayout(Layout):
    """to quote the nanogui docs:
    Special layout for widgets grouped by labels.

    This widget resembles a box layout in that it arranges a set of widgets vertically.
    All widgets are indented on the horizontal axis except for Label widgets, which are not indented.

    This creates a pleasing layout where a number of widgets are grouped under some high-level heading.
    """
    def __init__(self, int margin=15, int spacing=6, int groupSpacing=14, int groupIndent=20):
        self.ptr = new nanogui.GroupLayout(margin, spacing, groupSpacing, groupIndent)

cdef class AdvancedGridLayout(Layout):
    """to quote the nanogui docs:
    The is a grid layout with support for items that span multiple rows or columns, and per-widget alignment flags.
    Each row and column additionally stores a stretch factor that controls how additional space is redistributed.
    The downside of this flexibility is that a layout anchor data structure must be provided for each widget.

    for more details, see
    https://nanogui.readthedocs.io/en/latest/api/classnanogui_1_1AdvancedGridLayout.html?highlight=AdvancedGridLayout
    """
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
