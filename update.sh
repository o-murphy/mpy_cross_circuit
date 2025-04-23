#!/bin/bash
echo "Update mpy_cross tags"
git fetch --tags
ROOT=`pwd`
TAGS=`git tag --list`

function add_tag () {
	TAG=$1
	echo "Adding tag: $TAG to mpy_cross"
	pushd $ROOT
	cd micropython
	git checkout "$TAG" --force
	git reset --hard "$TAG"
	cd ..
	git checkout releases --force
	git add micropython
	git commit -m "micropython: $TAG"
	git tag "$TAG"
	popd
	echo ""
}

echo "Update micropython tags"
git checkout master
git reset --hard origin/master

git submodule update --init

git checkout releases --force
git reset --hard origin/master

cd micropython
git fetch --all
git fetch --tags

echo "Add tags to mpy_cross"

for TAG in `git tag --list`; do
	if GIT_DIR=../.git git rev-parse $TAG >/dev/null 2>&1
	then
		echo "Already tagged: $TAG"
	else
		add_tag "$TAG"
	fi
done

git checkout master --force
git reset --hard origin/master
GIT=`git rev-parse --short HEAD`
cd ..
git checkout master
git add micropython
git commit -m "micropython: $GIT" || true
# git push origin HEAD:master
# git push --tags origin
