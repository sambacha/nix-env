with import <nixpkgs> { };

let
  cutPoints = builtins.map (drv: drv.outPath) [
    nodejs
    python2
    python3
    coreutils
    openssl.out
    glibc
    bash
    gcc-unwrapped.lib
    bzip2.out
  ];

  mkContentsDrv = contents: symlinkJoin {
    name = "container-env";
    paths = (if builtins.isList contents then contents else [ contents ]);
  };

  mkLayers = contents: cutPoints: runCommand "closure-paths" {
    cutJSON = writeText "cuts" (builtins.toJSON cutPoints);
    passAsFile = [ "cutJSON" ];

    exportReferencesGraph.graph = contents;
    __structuredAttrs = true;
    PATH = "${coreutils}/bin:${python3}/bin";
    builder = builtins.toFile "builder" ''
      . .attrs.sh
      cat $cutJSON
      python3 ${./make_layers.py} --graph .attrs.json --cuts $cutJSON > outf
      mv outf ''${outputs[out]}
    '';
  } "";

  mkDockerImage = contents: let
    aggDrv = mkContentsDrv contents;
    layers = mkLayers aggDrv cutPoints;
  in layers;

  drv = (python3.withPackages(ps: [ ps.flake8 ]));

in mkDockerImage [ drv ]
