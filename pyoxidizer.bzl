def make_exe():
    if BUILD_TARGET_TRIPLE == "x86_64-unknown-linux-musl":
        flavor = "standalone_static"
    else:
        flavor = "standalone"
    dist = default_python_distribution(python_version="3.9", flavor=flavor)

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
