#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <string.h>
#include <time.h>

#define TIME_MACRO asctime(localtime(&now))

/*
    BEGIN--
    DO gcc -D_WIN32_WINNT=0x0501 -o brace.exe brace.c
    END--
*/

int killThread(HANDLE hProcess);

void chomp (char *s);

int main(int argc_, char **argv_)
{
    time_t now;
    time(&now);
    time(&now);
    char *tStr = TIME_MACRO;chomp(tStr);
    printf("* [%s] exception brace\n",tStr);
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    /*
        strtok on [braces]
    */

    int argc = 0;
    char *argv[1024];
    char *l = GetCommandLine();

    argv[argc++] = argv_[0];

    int i;
    int mLen = strlen(l);
    int startToken = 0;
    int lastTokenAddress;
    for(i = 0;i < mLen;i++)
    {
        if(l[i] == '[')
        {
            startToken = 1;
            lastTokenAddress = i + 1;
        }
        else if(l[i] == '[' && startToken == 1)
        {
            printf("* double open brace not allowed\n");
            return 0;
        }
        else if (l[i] == ']' && startToken == 1)
        {
            argv[argc] = (char *)malloc(i - lastTokenAddress + 1);
            memset(argv[argc],0,i - lastTokenAddress + 1);
            strncpy(argv[argc],l + lastTokenAddress, i - lastTokenAddress);
            printf("* setting argv[%d] to %s\n",argc, argv[argc]);
            argc++;
            startToken = 0;
        }
        else if( l[i] == ']')
        {
            printf("* closed brace without open brace not allowed\n");
            return 0;
        }
    }

    if(startToken == 1)
    {
        printf("* unclosed token not allowed\n");
        return 0;
    }

    /*
        strtok on [braces]
    */

    memset(&si,0,sizeof(si));
    memset(&pi,0,sizeof(pi));
    si.cb = sizeof(si);

    int firstException = 0;

    if(argc != 4)
    {
        printf("* usage: %s [program] [cmdline] [wdir]\n",argv[0]);
        return 0;
    }
    /*
    if(argv[1][0] != '[' || argv[1][strlen(argv[1]) - 1] != ']')
    {
        printf("* program must be surrounded by square brackets\n");
        return 0;
    }

    if(argv[2][0] != '[' || argv[2][strlen(argv[2]) - 1] != ']')
    {
        printf("* argv must be surrounded by square brackets\n");
        return 0;
    }

    if(argv[3][0] != '[' || argv[3][strlen(argv[3]) - 1] != ']')
    {
        printf("* wdir must be surrounded by square brackets\n");
        return 0;
    }
    */

    char *progName = argv[1];
    char *progArgv = argv[2];
    char *progWdir = argv[3];

    CreateProcess(progName,progArgv,NULL,NULL,FALSE,DEBUG_PROCESS,NULL,progWdir,&si,&pi);
    HANDLE hProcess = pi.hProcess;
    if(hProcess == NULL)
    {
        printf("* could not create process!\n");
        return 0;
    }
    // printf("* hProcess = %08x\n",(unsigned long )hProcess);

    DWORD ktID = 0;

    CreateThread (NULL, 1024, (LPTHREAD_START_ROUTINE) &killThread,hProcess, 0, &ktID);
    
    DEBUG_EVENT de;

    while(WaitForDebugEvent(&de,INFINITE))
    {
        if(de.dwDebugEventCode == EXCEPTION_DEBUG_EVENT)
        {
            if(firstException == 1)
            {
                if(de.u.Exception.dwFirstChance)
                {
                    printf("* First Chance Exception - exception code %08x\n",(unsigned long )de.u.Exception.ExceptionRecord.ExceptionCode );
                    ContinueDebugEvent (de.dwProcessId, de.dwThreadId, DBG_EXCEPTION_NOT_HANDLED);
                }
                else
                {
                    /*
                    if((unsigned long )de.u.Exception.ExceptionRecord.ExceptionCode == 0xe06d7363)
                    {
                        printf("* C++ Exception - passing\n");
                        ContinueDebugEvent (de.dwProcessId, de.dwThreadId, DBG_CONTINUE);
                    }
                    */
                    if(1)
                    {
                        time(&now);
                        tStr = TIME_MACRO;chomp(tStr);
                        printf("* [%s] terminating on exception\n", tStr);
                        CONTEXT c;
                        HANDLE hThread = OpenThread (THREAD_GET_CONTEXT + THREAD_SET_CONTEXT + THREAD_SUSPEND_RESUME, FALSE, de.dwThreadId);
                        c.ContextFlags = CONTEXT_FULL;
                        if(GetThreadContext (hThread, &c) == 0)
                        {
                           printf("* GetThreadContext failed. Probably check CONTEXT_FULL for your version of Windows. [%s:%d]\n",__FILE__,__LINE__);
                           exit(0);
                        }
                        printf("* [Exception Code: %08x]\n",(unsigned long )de.u.Exception.ExceptionRecord.ExceptionCode);
                        printf("* [EAX:%08X] [EBX:%08X] [ECX:%08X] [EDX:%08X]\n",(unsigned long )c.Eax, (unsigned long )c.Ebx, (unsigned long )c.Ecx, (unsigned long )c.Edx);
                        printf("* [EBP:%08X] [ESP:%08X] [EIP:%08X]\n",(unsigned long )c.Ebp, (unsigned long )c.Esp, (unsigned long )c.Eip);

                        ContinueDebugEvent (de.dwProcessId, de.dwThreadId, DBG_CONTINUE);
                        // DebugActiveProcessStop (de.dwProcessId);
                        TerminateProcess(hProcess,0);
                        CloseHandle (hProcess);
                        return 0;
                    }
                }
            }
            else
            {
                firstException = 1;
            }
            
        }
        else if(de.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT)
        {
            time(&now);
            tStr = TIME_MACRO;chomp(tStr);
            printf("* [%s] exiting normally\n", tStr);
            ContinueDebugEvent (de.dwProcessId, de.dwThreadId, DBG_CONTINUE);
            exit(0);
        }
        ContinueDebugEvent (de.dwProcessId, de.dwThreadId, DBG_CONTINUE);
    }
    
    return 0;
}

int killThread(HANDLE hProcess)
{
	time_t end;
	Sleep(10000);
    printf("* killing process %08x\n",(unsigned long )hProcess);
    TerminateProcess(hProcess,0);
	return 0;
}

void chomp (char *s)
{
  int i = 0;
  int stop = strlen (s);
  for (i = 0; i < stop; i++)
    {
      if (!(isprint (s[i])) || s[i] == '\r' || s[i] == '\n')
        {
          s[i] = 0;
          return;
        }
    }
}