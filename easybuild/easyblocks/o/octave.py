##
# Copyright 2009-2018 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/easybuilders/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for building and installing Octave, implemented as an easyblock

@author: Lekshmi Deepu (Juelich Supercomputing Centre)
@author: Kenneth Hoste (Ghent University)
"""
import os

import easybuild.tools.environment as env
from easybuild.easyblocks.generic.configuremake import ConfigureMake
from easybuild.tools.build_log import EasyBuildError
from easybuild.tools.modules import get_software_root
from easybuild.tools.run import run_cmd


EXTS_FILTER_OCTAVE_PACKAGES = ("octave --eval 'pkg list' | grep %(ext_name)s", '')


class EB_Octave(ConfigureMake):
    """Support for building/installing Octave."""

    def configure_step(self):
        """Custom configuration procedure for Octave."""

        libblas = os.getenv('LIBBLAS')
        liblapack = os.getenv('LIBLAPACK')
        if libblas and liblapack:
            self.cfg.update('configopts', '--with-blas="%s" --with-lapack="%s"' % (libblas, liblapack))
        else:
            raise EasyBuildError("$LIBBLAS and/or $LIBLAPACK undefined, use toolchain that includes BLAS/LAPACK")

        qt_root = get_software_root('Qt5') or get_software_root('Qt')
        if qt_root:
            self.log.info("Found Qt included as dependency, updating configure options accordingly...")
            qt_vars = {
                'LRELEASE': os.path.join(qt_root, 'bin', 'lrelease'),
                'MOC': os.path.join(qt_root, 'bin', 'moc'),
                'RCC': os.path.join(qt_root, 'bin', 'rcc'),
                'UIC': os.path.join(qt_root, 'bin', 'uic'),
            }
            for key, val in sorted(qt_vars.items()):
                self.cfg.update('configopts', "%s=%s" % (key, val))
        else:
            self.log.debug("No Qt included as dependency")

        super(EB_Octave, self).configure_step()

    def prepare_for_extensions(self):
        """Set default class and filter for Octave toolboxes."""
        # build and install additional packages with OctavePackage easyblock
        self.cfg['exts_defaultclass'] = 'OctavePackage'
        self.cfg['exts_filter'] = EXTS_FILTER_OCTAVE_PACKAGES
        super(EB_Octave, self).prepare_for_extensions()

    def sanity_check_step(self):
        """Custom sanity check for Octave."""
        custom_paths = {
            'files': ['bin/octave'],
            'dirs': [],
        }
        if self.cfg['exts_list']:
            custom_paths['dirs'].extend([
                os.path.join('share', 'octave', 'packages'),
                os.path.join('share', 'octave', 'packages-arch-dep'),
            ])

        custom_commands = ["octave --eval '1+2'"]

        super(EB_Octave, self).sanity_check_step(custom_paths=custom_paths, custom_commands=custom_commands)
