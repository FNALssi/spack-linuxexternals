import spack.config
import spack.util.spack_yaml as syaml
import spack.platforms
import os
import re
    
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
        "glibc",
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
            "target": [ "x86_64_v2" ],
            "providers" : {
               "blas": [ "openblas" ],
               "fftw-api": [ "ftw" ] ,
               "go-external-or-gccgo-bootstrap": [ "go-bootstrap" ],
               "gl": [ "glx" ],
               "glu": [ "mesa-glu" ],
               "golang": [ "go" ],
               "iconv": [ "glibc" ],
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
               "rpc": [ "glibc" ],
               "tbb": [ "intel-tbb-oneapi" ],
               "unwind": [ "libunwind" ],
               "uuid": [ "libuuid" ],
               "yacc": [ "bison" ],
             }
           }
         }
       }
 

    vers_re = r'^.*?[^0-9]([0-9][0-9]*\.[0-9.kp]*)[^0-9].*$'

    def __init__(self, packagelist = None):
        host_platform = spack.platforms.host()
        self.host_os = host_platform.operating_system('default_os')
        self.host_os = str(self.host_os)
        self.qalist = []
        if packagelist:
            self.packagelist = packagelist
        else:
            self.packagelist = __file__.replace('find_linux_externals.py','packagelist')

    def runversion(self, cmd):
        if cmd == "python":
            # take largest /usr/bin/python<n>
            l = glob.glob("/usr/bin/python*")
            l.sort()
            for f in l:
                if not l.find('config') >= 0:
                    cmd = l
        elif cmd == "autotools":
            cmd = "automake --version"
        elif cmd == "xlibtool":
            cmd = "automake --version"
        elif cmd == "texlive":
            cmd = "tex --version"
        elif cmd == "tcl":
            cmd = "echo info patchlevel | tclsh"
        elif cmd.find("proto") > 0:
            cmd = f"grep Version /usr/share/doc/xorgproto/{cmd}.txt"
        elif cmd.startswith("lib"):
            cmd = f"ls -l /usr/lib*/{cmd}.* | sed -e s/.*{cmd}.[a-z]*\\.//"
        else:
            cmd = f"{cmd} --version"

        with os.popen(f"{cmd} < /dev/null 2>&1", "r") as fin:
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

        if re.search("ubuntu", self.host_os):
            pkgcmd = f"apt list {pkg} 2>/dev/null | grep '\[installed\]'"

        elif re.search("almalinux|centos|fedora|rhel|scientific", self.host_os):
            pkgcmd = f"rpm -q {pkg} | tail -1 | grep -v 'is not installed'" 

        else:
            pkgcmd = ":"

        #print("pkgcmd: ", pkgcmd)
        with  os.popen(pkgcmd, "r") as pout:
            data = pout.read().strip()

        #print("before:" , data)
        data = re.sub(pkgfinder.vers_re,'\\1', data)
        #print("after:" , data)

        if not data:
            data = self.runversion(pkg)

        return data

    def get_prefix(self, pkg):
        if re.search("ubuntu", self.host_os):
            pkg_file_cmd = f"apt-file list {pkg} 2>/dev/null'"

        elif re.search("almalinux|centos|fedora|rhel|scientific", self.host_os):
            pkg_file_cmd =  f"rpm -ql {pkg}"

        else:
            return "/usr"

        res = "/usr"
        with os.popen(pkg_file_cmd) as flf:
            for line in flf:
                m = re.match(r"(.*)/(bin|share)/", line)
                if m:
                     res = m.group(1)
                     break
        return res

    def find_packages(self, initial):
        result = initial.copy()
        result.update(pkgfinder.base_packages)

        gccv = self.getv("gcc") 
        if gccv:
            comp = "%gcc@" + gccv
        else:
            comp = ""

        with open(self.packagelist,"r") as pfile:
            for line in pfile:

                line = line.strip()

                if re.match("^ *#", line):
                     continue

                #print("line: " + line)
                p,spp,dv = line.split(":")
                if not p:
                    p = spp

                #  turn p in to list pl by checking rpm -qa list
                # -- this should have an "apt" version...
                if p.find('[') >= 0 or p.find('|') >= 0 or p.find('(') >= 0:
                    #print("regex search...") 
                    p= '(' + p+ ')-[0-9]'
                    if not self.qalist:
                        if re.search("ubuntu", self.host_os):
                            cmd = "apt --installed list "

                        elif re.search("almalinux|centos|fedora|rhel|scientific", self.host_os):
                            cmd =  "rpm -qa"
                        else:
                            continue

                        with os.popen(cmd,"r") as rpmout:
                           self.qualist = rpmout.read().strip().split("\n")

                    pl = set([re.match(p,x).group(1) for x in self.qualist if re.match(p,x)])
                    #print("pl is " + repr(pl))
                    check_prefix = True

                else:
                    pl = [p]
                    check_prefix = False

                for pkg in pl:
                    dpkg = dv.replace('$0',pkg)
                    v = self.getv(pkg)

                    if not v:
                        print(f"Notice: no system-installed versions of {pkg} found (Spack package {spp})")
                        if dpkg == pkg:
                              print(f"May want to install {pkg}")
                        else:
                              print(f"May want to install {pkg} and {dpkg}")
                    else:
                        if not spp in result["packages"]:
                            result["packages"][spp] = {"externals": []}

                        if check_prefix:
                            prefix = self.get_prefix(pkg)
                        else:
                            prefix = "/usr"

                        buildable = not (spp in pkgfinder.flag_not_builable)
 
                        result["packages"][spp]["externals"].append(
                            {
                               "spec": f"{spp} @{v} {comp} os={self.host_os}", 
                               "prefix": prefix,
                               "buildable": buildable,
                           }
                        )
        return result
         
         
def find_linux_externals(args):

    config = spack.config.CONFIG
    filename = config.get_config_filename(args.scope, "packages") + ".new"
    if os.path.exists(filename):
        with open(filename, "r") as f:
             data = syaml.load(f.read())
        initial = data
    else:
        initial = {}
    pf = pkgfinder()
    data = pf.find_packages(initial)
    with open(filename, "w") as of:
        syaml.dump(data, of)
