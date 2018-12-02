IF LINUX:
    pass
ELIF WINDOWS:
    import datetime
    import sys


IF LINUX:
    pass  # use default error handling
          # todo make always do a core dump
ELIF WINDOWS:
    cdef extern from "windows.h":
        ctypedef struct CONTEXT
        ctypedef struct EXCEPTION_POINTERS:
            CONTEXT* ContextRecord
        void SetUnhandledExceptionFilter(long (__stdcall )(EXCEPTION_POINTERS *))
    cdef extern from "crash.c":
        void create_dump(void* context, char* filename)

    unhandled_exception_message = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
ERROR: UNHANDLED SYSTEM EXCEPTION
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
(probably a segfault)
dump written to {0}
"""
    cdef long __stdcall default_exception_handler(EXCEPTION_POINTERS* pointers):
        filename = '{}-{}.dmp'.format(sys.argv[0], datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S'))
        print(unhandled_exception_message.format(filename))
        create_dump(pointers, filename=filename.encode())
        exit(1)
    SetUnhandledExceptionFilter(default_exception_handler)
