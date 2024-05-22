
import os
import sys
prefix=os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(prefix, "linuxexternals"))
sys.path.append(os.path.join(os.environ["SPACK_ROOT"], "lib", "spack"))
sys.path.append(os.path.join(os.environ["SPACK_ROOT"], "lib", "spack", "external"))
sys.path.append(os.path.join(os.environ["SPACK_ROOT"], "lib", "spack", "external", "_vendoring"))

from find_linux_externals import pkgfinder

def test_runversion():
    pf = pkgfinder()
    v = pf.runversion("perl")
    print(f"for perl got '{v}'")
    assert(v.startswith("5."))

def test_getv():
    pf = pkgfinder()
    v = pf.getv("perl")
    print(f"for perl got '{v}'")
    assert(v.startswith("5."))

def test_pkgfinder_1():
    pf = pkgfinder(packagelist="packagelist1")
    pkgs = pf.find_packages({})
    print(repr(pkgs))
    assert("diffutils" in pkgs["packages"])
    assert("findutils" in pkgs["packages"])

def test_pkgfinder_2():
    pf = pkgfinder(packagelist="packagelist2")
    pkgs = pf.find_packages({})
    print(repr(pkgs))
    assert("gawk" in pkgs["packages"])
    assert("gmake" in pkgs["packages"])

def test_pkgfinder_re():
    pf = pkgfinder(packagelist="packagelist_re")
    pkgs = pf.find_packages({})
    print(repr(pkgs))
    assert("mpich" in pkgs["packages"])
    assert("krb5" in pkgs["packages"])

