###########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
###########################################################################

import sage.misc.interpreter

import preparser

interface_name  = 'sage'
interface       = None
num_lines       = 0

# TODO: Do this right?
magma_colon_equals = False

q_lines = []


def switch_interface_general(new_interface, verbose=True):
    global interface
    global interface_name
    if not (interface is None):
        interface._post_interact()
    interface = new_interface
    interface_name = new_interface.name().lower()
    sage.misc.interpreter.set_sage_prompt('%s'%interface_name)
    if verbose:
        print "\n  --> Switching to %s <-- \n"%interface
    interface._pre_interact()

def switch_interface(name, verbose=True):
    I = __import__('sage.interfaces.all',{},{},name)
    if not name in I.interfaces:
        raise RuntimeError, "Invalid interface %s"%name
    sage.misc.interpreter.PROMPT = '%s'%name
    
    global interface, interface_name
    interface_name = name
    if name == 'sage':
        interface = None
        if verbose:
            print "\n  --> Exiting back to Sage <-- \n"
    else:
        if not (interface is None):
            interface._post_interact()
        interface = I.__dict__[name]
        if verbose:
            print "\n  --> Switching to %s <-- \n"%interface
        interface._pre_interact()
        if name in ['kash']:
            interface('0')     # hack that works.
            
    sage.misc.interpreter.set_sage_prompt('%s'%interface_name)

def preparse_ipython(line, reset=True):
    """
    TESTS:
        
        Make sure #10933 is fixed
        
    ::
    
        sage: sage.misc.preparser_ipython.preparse_ipython("def foo(str):\n   time gp(str)\n\nprint gp('1')")
        'def foo(str):\n   __time__=misc.cputime(); __wall__=misc.walltime(); gp(str); print "Time: CPU %.2f s, Wall: %.2f s"%(misc.cputime(__time__), misc.walltime(__wall__))\n\nprint gp(\'1\')'

    """
    global num_lines
    global q_lines
    
    L = line.lstrip()
    if L.startswith('%'):
        # This should be installed as an Ipython magic command,
        # but I don't know how yet...
        L = L[1:].strip()
        import sage.interfaces.all
        if L.lower() in sage.interfaces.all.interfaces:
            switch_interface(L.lower())
            return "''"
        else:
            # only preparse non-magic lines
            return line

        
    if interface is None:
    #We could remove do_time=True if #10933 get's fixed upstream
        return preparser.preparse(line, reset=reset, do_time=True) 

    if L.startswith('?') or L.endswith('?'):
        L = L.strip('?')
        interface.help(L)
        return ''

    line = preparse_imports_from_sage(interface, line)
    line = line.rstrip()
    ends_in_backslash = line.endswith('\\')
    if ends_in_backslash:
        line = line.rstrip('\\')
        num_lines += 1
    else:
        if interface_name in ['gap', 'magma', 'kash', 'singular']:
            if not line.endswith(';'):
                line += ';'
        elif interface_name == 'mathematica':
            line = 'InputForm[%s]'%line

    if ends_in_backslash:
        q_lines.append(line)
    else:
        if len(q_lines) > 0:
            line = ''.join(q_lines) + line
        q_lines = []
        # TODO: do sage substitutions here 
        #t = interface._eval_line(line)
        t = interface.eval(line)
        
    import sage.misc.interpreter
    if ends_in_backslash:

        sage.misc.interpreter.set_sage_prompt('.'*len(interface_name))
    
    else:

        sage.misc.interpreter.set_sage_prompt('%s'%interface_name)
        #print t
        #__IPYTHON__.output_hist[len(__IPYTHON__.input_hist_raw)] = t

    # TODO: this is a very lazy temporary bug fix.
    # Nobody uses this logging stuff anymore, anyways, because
    # of the Sage notebook.
    try:
        return """logstr(%r)"""%t
    except UnboundLocalError:
        return 'logstr("")'


_v_ = None

def preparse_imports_from_sage(interface, line, locals={}):
    """
    The input line is being fed to the given interface.
    This function extracts any "sage(zzz)"'s, parses
    them, and replaces them by appropriate objects
    in the interface.   This is used for moving
    objects from Sage back into the interface.
    """
    import sage_eval
    i = line.find('%s('%interface_name)
    n = len(interface_name)
    if i == -1:
        i = line.find('sage(')
        n = 4
        if i == -1:
            return line
    j = i + line[i:].find(')')
    expr = line[i+n+1:j]
    expr = preparser.preparse(expr)
    s = 'import sage.misc.preparser_ipython; \
         sage.misc.preparser_ipython._v_ = sage.misc.preparser_ipython.interface(%s)'%expr
    #print s
    __IPYTHON__.runsource(s)
    #print _v_
    line = line[:i] + _v_.name() + line[j+2:]
    return line
    
