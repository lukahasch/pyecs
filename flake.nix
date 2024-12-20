{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = inputs@{ self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { inherit system; };
      in {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.pip
            python3Packages.virtualenv
            raylib
            dbus
            openssl
          ];
          nativeBuildInputs = with pkgs; [ pkg-config ];
          dbus = pkgs.dbus;
          shellHook = ''
            test -d .nix-venv || ${pkgs.python3.interpreter} -m venv .nix-venv
            source .nix-venv/bin/activate
            pip install -r requirements.txt
          '';
        };
      });
}
