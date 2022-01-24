def package_content() -> str:
    return """
// swift-tools-version:5.5

import PackageDescription

let package = Package(
    name: "API",
    platforms: [
        .macOS(.v12),
        .iOS(.v15)
    ],
    products: [
        .library(
            name: "API",
            targets: ["API"]),
    ],
    dependencies: [
        .package(url: "https://github.com/fillmula/qsparser-swift.git", from: "1.0.1")
    ],
    targets: [
        .target(
            name: "API",
            dependencies: [.product(name: "QSParser", package: "qsparser-swift")])
    ]
)
    """.strip() + '\n'
