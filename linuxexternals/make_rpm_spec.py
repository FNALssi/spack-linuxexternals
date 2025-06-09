#!/usr/bin/python3

import os
import os.path
import re
import sys

PREFIX=os.path.dirname(os.path.dirname(__file__))

PREFACE="""
Name:           deluxe_build_bundle
Version:        VERSION
Release:        1%{?dist}
Summary:        Every xxx-devel package you might need
Group:          Development/Languages
License:        GPLv2+
URL:            https://github.org/marcmengel/spack-linuxexternals/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
"""

SUFFIX="""
%description
Bundle of xxx-devel rpms you might need as Spack externals
%prep

%build

%install

%clean

%files

%changelog
* Mon Nov 22 2024 Marc Mengel <mengel@fnal.gov>
- First draft from fermi-spack-tools list
"""
def write_specfile(fname = "deluxe_build_bundle.spec", version="0.2"):
    with open(fname, "w") as of:
         of.write(PREFACE.replace("VERSION", version))
         for rpmname in get_rpmlist():
             of.write(f"Requires: {rpmname}\n")
         of.write(SUFFIX)

def get_yum_packages( yum_cmd ):
    candidates = []
       
    with os.popen(yum_cmd,"r") as yf:
         in_packages = False
         for line in yf.readlines():
             if line.find('Installed Packages') >= 0 or line.find('Available Packages') >= 0:
                in_packages = True
                continue
             if in_packages:
                pkg, rest = line.split('.',1)
                candidates.append(pkg)
    # print(f"get_yum_packages: yum_cmd: '{yum_cmd}' candidates: {repr(candidates)}")
    return candidates

def yum_expand(pat, devbits):
    yum_wc = pat
    #print(f"before: {yum_wc}")
    yum_wc = re.sub("\([^(]*\)\?", "*", yum_wc) 
    yum_wc = re.sub("\[[^[]*\]\*", "*", yum_wc) 
    yum_wc = re.sub("\.\*", "*", yum_wc) 
    yum_wc = re.sub(".\?", "*", yum_wc) 
    yum_wc = re.sub("[()]", "", yum_wc) 
    #print(f"after: {yum_wc}")
    yum_wc_devel = devbits.replace('$0',yum_wc)
    candidates = get_yum_packages(f"yum list '{yum_wc}' '{yum_wc_devel}'")
    res = []
    devpat = devbits.replace('$0',pat)
    for cand in candidates:
        if re.match(pat+'$', cand) or re.match(devpat + '$', cand):
            res.append(cand)
    return res

def get_rpmlist():
    packagelistf = f"{PREFIX}/linuxexternals/packagelist"
    rpmset = set()
    with open(packagelistf,"r") as pl:
         for line in pl.readlines():
             if line.strip()[0] == "#":
                 continue
             pat, spackname, devbits = line.strip().split(":")
             plist = yum_expand(pat, devbits)
             for p in plist:
                 rpmset.add(p)
    rpmlist = list(rpmset)
    rpmlist.sort()
    return rpmlist


if __name__ == '__main__':
   write_specfile()
