import os
import sys
import time
import pytest

# basic integration tests

@pytest.fixture
def mock_rpm():
    mockdir = __file__.replace("test_commandline.py","mock")
    os.environ["PATH"] = f'{mockdir}:{os.environ["PATH"]}'
    yield mockdir
    os.environ["PATH"] = os.environ["PATH"].replace(f"{mockdir}:","")
    return None

@pytest.fixture
def workenv():
    we = f"work_{os.getpid()}"
    os.system(f"spack env create {we}")
    yield we
    os.system(f"spack env remove -y {we}")
    return None

def test_help():
    with os.popen("spack linuxexternals --help", "r") as fin:
        data = fin.read()
    assert(data.find("--scope") >= 0)
    assert(data.find("--help") >= 0)

def test_minimal( workenv, mock_rpm):
    with os.popen(f"spack location --env {workenv}", "r") as fin:
         epath = fin.read().strip()
    print(f"environment path: {epath}")
    with os.popen(f"spack --config-scope={epath} linuxexternals --scope cmd_scope_0") as fin:
         data1 = fin.read()
    print(data1)

    with open(f"{epath}/packages.yaml", "r") as fin:
         data2 = fin.read()

    assert(data1.find("no system-installed versions of libXvMC") >= 0)
    assert(data1.find("May want to install libXvMC and libXvMC-devel") >= 0)
    assert(data2.find("spec: xproto @2022.2 ") >= 0)
    assert(data2.find("spec: texlive @20200406 ") >= 0)

    
