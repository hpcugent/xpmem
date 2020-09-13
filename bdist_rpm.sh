#!/bin/bash

function bdist_rpm {
    name=$1
    spec=$name.spec

    VERSION=$(grep "Version:.*[0-9]" $spec | tr -s " " |  awk '{print $2;}')
    RELEASE=$(grep "%global.*rel.*[-1-9]" $spec | tr -s " " | awk '{print $3}')

    echo $VERSION
    echo $RELEASE

    if [ "${RELEASE:-0}" -gt 1 ]; then
        SUFFIX=${VERSION}-${RELEASE}
    else
        SUFFIX=${VERSION}
    fi

    GITTAG=$(git log --format=%ct.%h -1)

    mkdir -p BUILD SOURCES SPECS RPMS BUILDROOT
    git archive --format=tar.gz -o "SOURCES/$name-${SUFFIX}.tar.gz" --prefix="$name-${SUFFIX}/" HEAD
    cp $spec "SPECS"
    rpmbuild --define "gittag ${GITTAG}" --define "_topdir $PWD" -ba SPECS/$spec
}

#bdist_rpm xpmem-kmod
#bdist_rpm xpmem-lib
bdist_rpm xpmem
