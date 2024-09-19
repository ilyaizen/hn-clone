{ pkgs }: {
  deps = [
    pkgs.python310Full
  ];
  env = {
    PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
    LANG = "en_US.UTF-8";
  };
}