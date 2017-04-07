from setuptools import setup, find_packages

setup(
        name = "whtmacro",
        version = "0.3",
        keywords = "documention",
        description = "help create document use HTML template",
        license = "GPLv2",
        author = "Fiathux Su",
        author_email = "fiathux@gmail.com",
        url = "https://github.com/fiathux/whtmacro",
        platforms = "any",
        packages = ["whtmacro"],
        entry_points = {
            "console_scripts":[
                "whtmacro = whtmacro:main"
                ]
            }
        )
