//
// Created by pc on 02/05/2018.
//

#include <Python.h>
# define MODINIT(name) PyInit_ ## name

PyMODINIT_FUNC MODINIT(cool_maths)(void);
PyMODINIT_FUNC MODINIT(very_cool_maths)(void);