import spack.config
import spack.util.spack_yaml as syaml
import os
import re
import spack.platforms
    
class pkgfinder:
    flag_not_builable = [
        "bdftopcf",
        "damageproto",
        "diffutils",
        "expat",
        "findutils",
        "font-util",
        "gdbm",
        "gettext",
        "libc",
        "libfontenc",
        "libice",
        "libx11",
        "libxau",
        "libxcb",
        "libxdamage",
        "libxdmcp",
        "libxext",
        "libxfixes",
        "libxfont",
        "libxkbcommon",
        "libxmu",
        "libxpm",
        "libxrandr",
        "libxrender",
        "libxshmfence",
        "libxt",
        "libxv",
        "libxvmc",
        "libxxf86vm",
        "mesa-glu",
        "mkfontdir",
        "mkfontscale",
        "motif",
        "openssl",
        "pkg-config",
        "pkgconf",
        "tar",
        "tcl",
        "tk",
        "xcb-util-image",
        "xcb-util-keysyms",
        "xcb-util-renderutil",
        "xcb-util-wm",
        "xextproto",
        "xorg-server",
        "xproto",
        "xproxymanagementprotocol",
        "xrandr",
        "xtrans",
        "zlib"
    ]

    base_packages = {
       "packages": {
          "all": {
            "compiler": ["gcc", "clang"],
            "target": "x86_64_v2",
            "providers" : {
               "blas": [ "openblas" ],
               "fftw-api": [ "ftw" ] 
               "go-external-or-gccgo-bootstrap": [ "go-bootstrap" ],
               "gl": [ "glx" ],
               "glu": [ "mesa-glu" ],
               "golang": [ "go" ],
               "iconv": [ "libc" ],
               "java": [ "openjdk" ],
               "jpeg": [ "libjpeg-turbo" ],
               "lapack": [ "openblas" ],
               "libglx": [ "mesa+glx" ],
               "libllvm": [ "llvm" ],
               "libosmesa": [ "mesa+osmesa" ],
               "mariadb-client": [ "mariadb-c-client" ],
               "mysql-client": [ "mariadb-c-client" ],
               "pbs": [ "torque" ],
               "pkgconfig": [ "pkg-config", "pkgconf" ],
               "rpc": [ "libc" ],
               "tbb": [ "intel-tbb-oneapi" ],
               "unwind": [ "libunwind" ],
               "uuid": [ "libuuid" ],
               "yacc": [ "bison" ],
             }
           }
         }
       }
 

    vers_re = r'^.*[^0-9.]([0-9][0-9]*\.[0-9.kp]*).*$'

    def runversion(self, cmd):
        if cmd == "python":
            # take largest /usr/bin/python<n>
            l = glob.glob("/usr/bin/python*")
            l.sort()
            for f in l:
                if not l.find('config') >= 0:
                    cmd = l
        elif cmd == "autotools":
            cmd = "automake"
        elif cmd == "xlibtool":
            cmd = "automake"
        elif cmd == "tcl":
            cmd = "echo info patchlevel | tclsh"
        elif cmd.find("proto") > 0:
            cmd = f"grep Version /usr/share/doc/xorgproto/{cmd}.txt"
        elif cmd.startswith("lib"):
            cmd = f"ls -l /usr/lib*/{cmd}.* | sed -e s/.*{cmd}.[a-z]*\.//"

        with os.popen(f"{cmd} --version < /dev/null 2>&1", "r") as fin:
            data = fin.read().split('\n')
        first = ""
        for line in data:
            if not line:
                 continue
            if re.search("error:|for help|not found|illegal|invalid|usage:|--version|-v", line):
                 continue
            first = line
            break  
        first = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|/).*', "", first)
        first = re.sub(cmd, "", first, flags=re.I)
        first = re.sub(pkgfinder.vers_re,'\\1', first)
        return first

    def getv(self, pkg):
        host_os = spack.platfoms.host().operating_sytem("default_os")

        if re.search("ubuntu", host_os):
            pkgcmd = f"apt list {pkg} 2>/dev/null | grep '\[installed\]'"

        elif re.search("almalinux|centos|fedora|rhel|scientific", host_os):
            pkgcmd = f"rpm -q {pkg} | tail -1 | grep -v 'is not installed'" 

        else:
            pkgcmd = ":"

        with( os.popen(pkgcmd, "r") as pout:
            data = pout.read().strip()

        data = re.sub(pkgfinder.vers_re,'\\1', data)

        if not data:
            data = runversion(pkg)

        return data

    def find_packages(self):
        result = pkgfinder.base_packages.copy()
        packagelist = __file__.replace('externalsys.py','packagelist')
        with open(packageslist,"r" as pfile:
            for line in pfile:

                line = line.strip()

                if re.match("^ *#", line):
                     continue

                p,spp,dv = line.split(":")

                #  turn p in to list pl by checking rpm -qa list
                # -- this should have an "apt" version...
                if p.find('[') >= 0 or p.find('(') >= 0:
                    if not qalist:
                        cmd = f"rpm -qa" 
                        with os.popen(cmd,"r") as rpmout:
                           qualist = rpmout.read().strip().split("\n")
                    pl = [x for x in qualist if re.match(p,x)]
                else:
                    pl = [p]

                for pkg in pl:
                    dpkg = dv.replace('$0',pkg)
                    v = self.getv(pkg)

                    if not v:
                        print(f"Notice: no system-installed versions of {pkg} found (Spack package {spp})")
                        if dpkg == pkg:
                              print("May want to install {pkg}")
                        else:
                              print("May want to install {pkg} and {dpkg}")
                    else:
                        if not spp in result["packages"]:
                            result["packages"][spp] = {"externals": []}

                        buildable = not (spp in pkgfinder.flag_not_builable)
 
                        result["packages"][spp]["externals"].append(
                            {
                               "spec": f"{spp} @{v} %{comp} os={os}", 
                               "prefix": "/usr",
                               "buildable": buildable,
                           }
                        )
        return result
         
         
def find_externals(parser):
    config = spack.config.CONFIG
    filename = config.get_config_filename(args.scope, "packages")
    pf = packagefinder()
    data = pf.find_packages()
    with open(filename, "w") as of:
        syaml.dump(data, of)
