net_download()
{
    local url=$1
    local output=$2
    local headers
    local checksum

    [ -n "${url}" -a -n "${output}" ] || return 1

    headers=$(wget -S -O "${output}" "${url}" 2>&1 >/dev/null)

    if [ $? != 0 ]; then
        rm -f "${output}"

        return 1
    fi

    checksum=$(echo "${headers}" | grep -i "X-Checksum" | awk '{print $2}')

    if [ -z "${checksum}" ] || [ $(hash_file "${output}") != "${checksum}" ]; then
        rm -f "${output}"

        return 1
    fi

    return 0
}
