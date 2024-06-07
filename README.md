

## Spack-linuxexternals

a [Spack extension](https://spack.readthedocs.io/en/latest/extensions.html#custom-extensions) to find external/system pacakges using linux package management tools; this finds many more packages than the current spack external find'
This generates an updated packages.yaml file in the requested scope.

### Usage

In most cases you can just do:

  spack linuxexternals

but you can specify --scope scope-name to specify where the packages.yaml
will be generated.

### Installation

After cloning the repository somewhere, See the [Spack docs](https://spack.readthedocs.io/en/latest/extensions.html#configure-spack-to-use-extensions) on adding the path to config.yaml under 'extensions:'
