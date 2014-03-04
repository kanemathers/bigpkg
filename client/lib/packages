import "index"
import "net"

package_install()
{
    local package=$1
    local build
    local src
    local dst
    local filename

    [ -n "${package}" ] || return 1

    if grep -q "^${package}" $INDEX_LOCAL; then
        # TODO: upgrade package
        echo "error: target already installed: ${package}" >&2

        return 1
    fi

    src=$(package_download $package) || return 1
    build="${BUILD_DIR}/${package}"

    mkdir $build || return 1

    # TODO: this sucks. find out why tars ``-C`` flag isn't working
    cd $build
    tar xzf $src 2>/dev/null
    cd $CWD

    # BUG: need package name written to local db so we can roll back on error
    # below. but if there's no files in the build dir, ``remove`` will error
    # and the package will be stuck (can't rm it).
    grep "^${package}" $INDEX_REMOTE >> $INDEX_LOCAL

    for i in $(find $build -type f); do
        filename="${i:${#build} + 1}"
        dst=$(dirname "${PREFIX}/${filename}")

        echo "${filename}" >> "${CWD}/pkgs/${package}.db"

        mkdir -p $dst || (remove $package; return 1)
        mv -f $i $dst || (remove $package; return 1)
    done

    return 0
}

package_remove()
{
    local package=$1

    [ -n "${package}" ] || return 1

    if ! grep -q "^${package}" $INDEX_LOCAL; then
        echo "error: target not found: ${package}" >&2

        return 1
    fi

    # TODO: remove stale folders... somehow
    while read line; do
        rm -f "${PREFIX}/${line}" || return 1
    done < "${CWD}/pkgs/${package}.db" || return 1

    rm -f "${CWD}/pkgs/${package}.db"
    sed "/^${package}/d" $INDEX_LOCAL > $INDEX_LOCAL

    return 0
}

package_upgrade()
{
    local package
    local checksum
    local remote

    while read line; do
        package=$(echo "${line}" | awk '{print $1}')
        checksum=$(echo "${line}" | awk '{print $2}')

        # failed grep means package has been rm'd from upstream
        remote=$(grep "^${package}" $INDEX_REMOTE) || continue

        if [ $(echo "${remote}" | awk '{print $2}') == "${checksum}" ]; then
            continue
        fi

        # TODO: separate building and installing so we can ensure upgrade
        # will apply before removing the current version
        remove $package
        install $package
    done < $INDEX_LOCAL || return 1

    return 0
}

package_download()
{
    local package=$1
    local url
    local dst

    [ -n "${package}" ] || return 1

    url="${SERVER}/packages/${package}.tar.gz"
    dst="${PKG_DIR}/${package}.tar.gz"

    if ! grep -q "^${package}" $INDEX_REMOTE; then
        echo "error: target not found: ${package}" >&2

        return 1
    fi

    while ! net_download $url $dst; do
        echo "error: failed to fetch: ${url}. retrying..." >&2

        sleep 5
    done

    echo "${dst}"

    return 0
}

hash_file()
{
    local path=$1
    local checksum

    [ -n "${path}" ] || return 1

    checksum=$(md5sum "${path}" 2>/dev/null | awk '{print $1}') || return 1

    echo "${checksum}"

    return 0
}
