from sotooncli.cache_utils import CacheUtils
from sotooncli.repo import CliRepo
from sotooncli.settings import USE_CACHE


def main():
    cache = CacheUtils(use_cache=USE_CACHE).get_cache()
    repo = CliRepo(cache)
    cli = repo.get_cli()
    cli()


if __name__ == "__main__":
    main()
