# Build environment for Neue Comet.
#
# The build is pure Python: `make venv` creates build/venv from Pipfile.lock
# and everything after that (fontmake, ufo2ft, fontbakery, psautohint,
# ttfautohint) runs from it. So the image is a slim Python plus the few
# system tools the Makefile shells out to.
#
# Podman:
#   podman build -t neue-comet .
#   podman run --rm -it --userns=keep-id \
#     -v "$PWD:/workspace:Z" -w /workspace neue-comet make all
#
# --userns=keep-id is required under rootless Podman: without it the
# container's uid 1000 maps to a subordinate uid rather than to your host uid,
# and every target fails with "Permission denied" creating build/.
# misc/tools/podmanmake wraps all of this, including the flag.
FROM docker.io/library/python:3.8-slim

# The Debian codename is deliberately not pinned in the tag. Python 3.8 is
# pinned by Pipfile (`requires.python_version`) and that is what has to hold --
# pipenv refuses to install against a 3.8 lock on anything else. The Debian
# release underneath is free to move; only the interpreter version matters.
#
# Do not move the tag to 3.9+ without updating Pipfile and Pipfile.lock
# together. The lock's `[requires]` is what pipenv validates against, and the
# pinned fontbakery/ttfautohint versions in it were resolved for 3.8.

# zip: make zip_beta / misc/makezip2.sh shell out to it.
# build-essential: several ufo2ft/fontbakery dependencies still ship as
#   sdists, and skia-pathops has no wheel for every platform.
# git: the build derives the font's unique ID and the release archive name
#   from the commit hash (`git rev-parse --short=10 HEAD`).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      git \
      make \
      zip \
 && rm -rf /var/lib/apt/lists/*

# Run as a non-root user whose uid/gid match the host, so the bind-mounted
# checkout stays writable without a second layer of sudo. Defaults match the
# common first local user; override for other machines:
#   podman build --build-arg UID=1001 --build-arg GID=1001 -t neue-comet .
ARG USERNAME=node
ARG UID=1000
ARG GID=1000

RUN groupadd --gid "${GID}" "${USERNAME}" \
 && useradd --uid "${UID}" --gid "${GID}" --create-home --shell /bin/bash "${USERNAME}"

WORKDIR /workspace

# Deliberately no PIPENV_* variables here. The Makefile owns the venv: it
# creates build/venv, exports VIRTUAL_ENV and PATH, and expects pipenv to
# adopt that environment and install into it. Setting PIPENV_VENV_IN_PROJECT
# or PIPENV_IGNORE_VIRTUALENVS makes pipenv build its own .venv alongside
# build/venv instead, and then every tool (fontmake, fontbakery, psautohint)
# goes missing from the PATH the Makefile exports.
#
# Just the cache location, so fontbakery and pip do not write into $HOME on
# the bind mount and dirty the checkout with dotfiles.
ENV XDG_CACHE_HOME=/home/node/.cache \
    PYTHONDONTWRITEBYTECODE=1

USER ${USERNAME}

CMD ["bash"]
