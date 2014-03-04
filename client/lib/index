index_fetch()
{
    local index

    index=$(wget -O - "${SERVER}/packages" 2>/dev/null) || return 1

    echo "${index}"

    return 0
}

index_update()
{
    local index

    index=$(index_fetch)

    if [ $? != 0 ]; then
        echo "error: failed to fetch index" >&2

        return 1
    fi

    rm -f "${INDEX_REMOTE}" || return 1
    echo "${index}" > "${INDEX_REMOTE}" || return 1

    return 0

}
