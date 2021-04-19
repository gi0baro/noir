.PHONY: _path_build compile pack sign

ARCH_LINUX := x86_64-unknown-linux-musl
ARCH_MAC := x86_64-apple-darwin
ARCH_WIN := x86_64-pc-windows-msvc
BUILD_VERSION := latest

_path_build:
	$(eval BUILDPATH := build/${ARCH}/release/install)

clean_build: _path_build
	@rm -rf ${BUILDPATH}

clean_dist:
	@rm -rf dist

build_linux: ARCH := ${ARCH_LINUX}
build_linux: compile

build_mac: ARCH := ${ARCH_MAC}
build_mac: compile sign

build_win: ARCH := ${ARCH_WIN}
build_win: compile

compile: _path_build clean_build clean_dist
	pyoxidizer build --release --target-triple=${ARCH}

sign: _path_build
	@codesign -s - ${BUILDPATH}/noir

pack_linux: ARCH := ${ARCH_LINUX}
pack_linux: pack

pack_mac: ARCH := ${ARCH_MAC}
pack_mac: pack

pack_win: ARCH := ${ARCH_WIN}
pack_win: pack

pack: _path_build clean_dist
	@mkdir -p dist
	@cd ${BUILDPATH} && tar -czvf noir-${BUILD_VERSION}-${ARCH}.tar.gz *
	@mv ${BUILDPATH}/noir-${BUILD_VERSION}-${ARCH}.tar.gz dist
	@openssl sha256 < dist/noir-${BUILD_VERSION}-${ARCH}.tar.gz | sed 's/^.* //' > dist/noir-${BUILD_VERSION}-${ARCH}.sha256sum
	@cat dist/noir-${BUILD_VERSION}-${ARCH}.sha256sum
