import spack.config
import spack.extensions.externalsys.externalsys as esys


def setup_parser(subparser):

    scopes = spack.config.scopes()

    subparser.add_argument(
        "--scope",
        choices=scopes,
        metavar=spack.config.SCOPES_METAVAR,
        default=spack.config.default_modify_scope("packages"),
        help="configuration scope to modify",
    )

    
def exernalsys(parser, args):
    esys.find_externals(parser)
