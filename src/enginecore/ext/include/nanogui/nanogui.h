/*
    nanogui/nanogui.h -- Pull in *everything* from NanoGUI

    NanoGUI was developed by Wenzel Jakob <wenzel.jakob@epfl.ch>.
    The widget drawing code is based on the NanoVG demo application
    by Mikko Mononen.

    All rights reserved. Use of this source code is governed by a
    BSD-style license that can be found in the LICENSE.txt file.
*/

#pragma once

// disable warnings for nanogui (added by biglizard, not the author,
// because msvc 2015 (which i have to use) doesnt support -isystem) 
#ifdef _WIN32
#pragma warning( push, 0 )
#endif

#include <nanogui/common.h>
#include <nanogui/widget.h>
#include <nanogui/screen.h>
#include <nanogui/theme.h>
#include <nanogui/window.h>
#include <nanogui/layout.h>
#include <nanogui/label.h>
#include <nanogui/checkbox.h>
#include <nanogui/button.h>
#include <nanogui/toolbutton.h>
#include <nanogui/popup.h>
#include <nanogui/popupbutton.h>
#include <nanogui/combobox.h>
#include <nanogui/progressbar.h>
#include <nanogui/entypo.h>
#include <nanogui/messagedialog.h>
#include <nanogui/textbox.h>
#include <nanogui/slider.h>
#include <nanogui/imagepanel.h>
#include <nanogui/imageview.h>
#include <nanogui/vscrollpanel.h>
#include <nanogui/colorwheel.h>
#include <nanogui/graph.h>
#include <nanogui/formhelper.h>
#include <nanogui/stackedwidget.h>
#include <nanogui/tabheader.h>
#include <nanogui/tabwidget.h>
#include <nanogui/glcanvas.h>


#ifdef _WIN32
#pragma warning( pop ) 
#endif
