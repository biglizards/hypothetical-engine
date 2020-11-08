#include <windows.h>
#include <Dbghelp.h>

void create_dump(EXCEPTION_POINTERS* pointers, char* filename)
{
    HANDLE file = CreateFileA(filename, GENERIC_WRITE, FILE_SHARE_READ, 0, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);

    MINIDUMP_EXCEPTION_INFORMATION exceptionInfo;
    exceptionInfo.ThreadId = GetCurrentThreadId();
    exceptionInfo.ExceptionPointers = pointers;
    exceptionInfo.ClientPointers = FALSE;

    // man you've gotta pass a *lot* of arguments to this thing
    // i mean, you'd think windows would know what the process calling its api is, for one
    MiniDumpWriteDump(
    GetCurrentProcess(), GetCurrentProcessId(), file, MiniDumpNormal,
    pointers ? &exceptionInfo : NULL, NULL, NULL
    );

    CloseHandle(file);
}