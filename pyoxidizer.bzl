def make_exe():
    distributions = {
        "x86_64-unknown-linux-musl": PythonDistribution(
            sha256="e711f6a063efb665e425f4f071c75f2a8c107f599c99130ecfff2b0532f7b804",
            url="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13+20240224-x86_64-unknown-linux-musl-noopt-full.tar.zst",
        ),
        "aarch64-unknown-linux-gnu": PythonDistribution(
            sha256="ab7195f04182d94aa675e738b6cf8affd4e897e7be7f02224cf36865194be344",
            url="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13+20240224-aarch64-unknown-linux-gnu-noopt-full.tar.zst"
        ),
        "x86_64-apple-darwin": PythonDistribution(
            sha256="178dda6f63f8bf9438649743ab659f47f5f379b36b6fcc51491f49c8c01f4615",
            url="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13+20240224-x86_64-apple-darwin-pgo-full.tar.zst"
        ),
        "aarch64-apple-darwin": PythonDistribution(
            sha256="5f90a26379f423de40c1be6c06fbc68b82f8b09f43e657932a48df30d3f5dba4",
            url="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13+20240224-aarch64-apple-darwin-pgo-full.tar.zst"
        ),
        "x86_64-pc-windows-msvc": PythonDistribution(
            sha256="6a2c8f37509556e5d463b1f437cdf7772ebd84cdf183c258d783e64bb3109505",
            url="https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.10.13+20240224-x86_64-pc-windows-msvc-shared-pgo-full.tar.zst"
        )
    }

    dist = distributions[BUILD_TARGET_TRIPLE]

    policy = dist.make_python_packaging_policy()
    policy.resources_location_fallback = "filesystem-relative:lib"

    python_config = dist.make_python_interpreter_config()
    python_config.module_search_paths = ["$ORIGIN/lib"]
    python_config.run_module = "noir.cli"

    exe = dist.to_python_executable(
        name="noir",
        packaging_policy=policy,
        config=python_config,
    )
    exe.add_python_resources(exe.pip_install(["."]))

    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()

def make_install(exe):
    files = FileManifest()
    files.add_python_resource(".", exe)
    return files


register_target("exe", make_exe)
register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)
register_target("install", make_install, depends=["exe"], default=True)

resolve_targets()
