#ifdef _WIN32
// on windows, python defines hypot as _hypot
// but _hypot isn't defined outside of C98
#define _hypot hypot
#endif
#include <Python.h>

#include <iostream>
#include "cy_stuff/cool_maths.h"
#include "cy_stuff/heck.c"


int main() {
#ifdef _WIN32
    // on windows the python distribution is supplied
    Py_SetPath(L"python36.zip");
#endif
    PyImport_AppendInittab("cool_maths", PyInit_cool_maths);
    PyImport_AppendInittab("very_cool_maths", PyInit_very_cool_maths);
    Py_Initialize();
    PyImport_ImportModule("cool_maths");
    PyImport_ImportModule("very_cool_maths");

    std::cout << cool_add(3, 5) << std::endl;

    Py_Finalize();
    return 0;
}