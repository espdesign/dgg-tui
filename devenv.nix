{
  pkgs,
  lib,
  config,
  ...
}: {
  # https://devenv.sh/packages/
  packages = [
    # Include the `websockets` package in the system environment if needed globally.
    # Otherwise, rely on pip to install it in the venv.
  ];

  # https://devenv.sh/languages/
  languages = {
    python = {
      enable = true;
      venv.enable = true;
      venv.requirements = pkgs.lib.strings.concatStringsSep "\n" [
        "python-dotenv"
        "websockets"
      ];
    };
  };

  # See full reference at https://devenv.sh/reference/options/
}
