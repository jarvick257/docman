class Config:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser(
            "config",
            description="Opens docman config in editor (uses $EDITOR environment variable).",
        )
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc):
        from docman.utils import get_config_path
        import os

        if "EDITOR" in os.environ:
            editor = os.environ["EDITOR"]
        else:
            print("EDITOR environment variable not set. Falling back to vi.")
            editor = "vi"
        os.system(f"{editor} {get_config_path()}")
        return None, 0
