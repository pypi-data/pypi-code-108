def pytest_addoption(parser):
    parser.addoption(
        "--shard-size", default=10, type=int, help="Size of the Read Shard file in MB",
    )
    parser.addoption(
        "--shard-path", default="/tmp/payload", help="Path of the Read Shard file",
    )
    parser.addoption(
        "--shard-count",
        default=2,
        type=int,
        help="Number of Read Shard files for lookup tests",
    )
    parser.addoption(
        "--object-max-size",
        default=10 * 1024,
        type=int,
        help="Maximum size of an object in bytes",
    )
    parser.addoption(
        "--lookups", default=10, type=int, help="Number of lookups to perform",
    )
