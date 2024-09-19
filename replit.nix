{ pkgs }: {
  deps = [
    pkgs.python310Full
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.python310Full
    ];
    PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
    LANG = "en_US.UTF-8";
  };
}