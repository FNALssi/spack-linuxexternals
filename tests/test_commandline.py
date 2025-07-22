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

@pytest.fixture
def workdir():
    we = f"/tmp/work_{os.getpid()}"
    os.mkdir(we)
    yield we
    os.system(f"rm -rf {we}")
    return None

def test_help():
    with os.popen("spack linuxexternals --help", "r") as fin:
        data = fin.read()
    assert(data.find("--scope") >= 0)
    assert(data.find("--help") >= 0)

def test_minimal( workdir, mock_rpm):
    print(f"workdir: {workdir}")
    with os.popen(f"spack --config-scope={workdir} linuxexternals --scope cmd_scope_0") as fin:
         data1 = fin.read()
    print(data1)

    with open(f"{workdir}/packages.yaml", "r") as fin:
         data2 = fin.read()

    assert(data1.find("no system-installed versions of autogen") >= 0)
    assert(data1.find("want to install autogen") >= 0)
    assert(data2.find("spec: xproto @2022.2 ") >= 0)
    assert(data2.find("spec: texlive @20200406 ") >= 0)

    
