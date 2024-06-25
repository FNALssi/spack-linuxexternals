import sys
import spack.config
from  spack.extensions import linuxexternals as lext

description = "find many external packages on linux systems "
section = "basic"
level = "short"

def setup_parser(subparser):

    scopes = spack.config.scopes()

    subparser.add_argument(
        "--scope",
        choices=scopes,
        metavar=spack.config.SCOPES_METAVAR,
        default=spack.config.default_modify_scope("packages"),
        help="configuration scope to modify",
    )

    
def linuxexternals(parser, args):
    #print("parser is " + repr(parser) + "args: " + repr(args))
    lext.find_linux_externals(args)
