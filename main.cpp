#ifdef _WIN32
// on windows, python defines hypot as _hypot
// but _hypot isn't defined outside of C98
#define _hypot hypot
#endif
#include <Python.h>

#include <iostream>
#include "bridge.h"


int main() {
#ifdef _WIN32
    // on windows the python distribution is supplied
    Py_SetPath(L"python36.zip");
#endif
    PyImport_AppendInittab("wrongname", PyInit_bridge);
    Py_Initialize();
    PyImport_ImportModule("wrongname");

    std::cout << add(3, 4) << std::endl;
    Py_Finalize();
    return 0;
}