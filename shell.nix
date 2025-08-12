{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.flask
    python311Packages.flask-cors
    python311Packages.pillow
    python311Packages.tqdm
    python311Packages.numpy
    python311Packages.werkzeug
    python311Packages.gunicorn
  ];
} 