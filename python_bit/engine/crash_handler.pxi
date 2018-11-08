IF LINUX:
    from libc.stdio cimport printf, sprintf
    from libc.stdlib cimport system
    from libc.signal cimport signal, SIGSEGV, sighandler_t, SIG_DFL
    from posix.unistd cimport getpid
    from posix.signal cimport kill
ELIF WINDOWS:
    import datetime
    import sys


IF LINUX:
    cdef extern from "execinfo.h":
        int backtrace (void **buffer, int size)
        char ** backtrace_symbols (void* const *buffer, int size)
        void backtrace_symbols_fd (void* const *buffer, int size, int fd)


    cdef void handler(int signum):
        print("oh no a segfault (value is", signum, "btw)")
        cdef:
            void* traces[10]
            int size
            char** messages
            int p
            char command[256]
        size = backtrace(traces, 10)
        messages = backtrace_symbols(traces, size)
        print(size, [message for message in messages[:size]])

        for i in range(2, size):
            printf("[bt] %s\n", messages[i])
            p = 0
            while messages[i][p] != ord('(') and messages[i][p] != ord(' ') and messages[i][p] != 0:
                p += 1

            name = messages[i][:p]
            addr = messages[i][p+1:p+messages[i][p:].find(b')')]
            if name.startswith(b'python'):
                continue
            sprintf(command, "addr2line %s -e %s \n", addr, name)
            if system(command) != 0:
                print("call to addr2line failed, aborting")
                break

        # remove the handler and re-raise the exception (to dump the core)
        signal(signum, SIG_DFL)
        kill(getpid(), signum)
    # end of handler function
    # un-comment this line to enable the segfault handler
    # hint: dont do that its not very good
    #signal(SIGSEGV, <sighandler_t>handler)

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
