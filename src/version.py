import subprocess
from functools import lru_cache

__app_name__ = "TG-Naladka"
__version__ = "0.3.1"

GIT_REVISION_CMD: tuple[str, ...] = ("git", "rev-list", "--count", "HEAD")


@lru_cache(maxsize=1)
def git_revision() -> str:
    """
    Возвращает количество коммитов Git в виде строки ревизии (например, «r123»).

    Если Git недоступен, используется значение из переменной среды или «r0».
    """

    try:
        count = subprocess.check_output(
            GIT_REVISION_CMD,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
        if not count.isdigit():
            return "r0"
        return f"r{count}"
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return "r0"


__revision__ = git_revision()
__full_version__ = f"{__app_name__}-{__version__}+{__revision__}"
