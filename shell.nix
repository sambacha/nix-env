with import <nixpkgs> {};

mkShell {
  buildInputs = [
    (python3.withPackages(ps: [
      ps.nixpkgs
    ]))
  ];
}
