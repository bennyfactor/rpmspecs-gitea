rpmspecs-gitea
^^^^^^^^^^^^^^

This is the RPM spec files that I have created for gitea. I am not affiliated with the gitea project and only provide this as a service.

.. contents::

Information
-----------

**Note:** I am not responsible for system damages, break-ins, or faulty code of the software that can cause the formerly listed. Always develop and test in an isolated environment at all times. **Always keep SELinux enabled.**

Frequently Asked Questions
--------------------------

Do you have any SRPMS available?
++++++++++++++++++++++++++++++++

They'll normally be available from my copr builds, if you are interested in making changes and using mock for yourself.

Have any documentation or guides?
+++++++++++++++++++++++++++++++++

If you're starting out rpm packaging, please consider reading the following documentation. The packaging guidelines may seem strict, but they are deemed best practices if you are considering on being a package maintainer (sponsored or not). Keep in mind, **I am always learning**. I am in no way an expert, nor do I claim to be.

`FHS <http://www.pathname.com/fhs/>`_

`Fedora: Fedora Packaging Guidelines <https://docs.fedoraproject.org/en-US/packaging-guidelines/>`_

`Fedora: Creating RPM Packages <https://docs.fedoraproject.org/en-US/package-maintainers/Packaging_Tutorial_GNU_Hello/>`_

What you should get from the above is there are specific guidelines that should be followed, for maintainability, portability, and easy review. My RPM specs will have an FAQ of the "purpose". 

Do you have any repositories?
+++++++++++++++++++++++++++++

Yes, I do. I have two, actually. I have a copr and a personal repository.

`Copr <https://copr.fedorainfracloud.org/coprs/nalika/>`_

Do you take requests?
+++++++++++++++++++++

I normally don't. But, if what you're asking for doesn't have an RPM or project in copr, I'll consider it based on what it is, and if it fits licensing and guidelines. You can drop me an email or a line here and I will get back to you.

Do you package for other systems?
+++++++++++++++++++++++++++++++++

At this present time, I do not. I have considered packaging for Ubuntu or OpenSUSE. However those, much like Arch, already have plenty of maintainers with tons upon tons of packages (up to date or not) and their own build systems similar to Fedora. So some of the packages you may see here may already exist for those distributions in base or extra repositories they provide.

About this fork
---------------

This fork (bennyfactor/rpmspecs-gitea) does not compile Gitea. The spec downloads
the upstream prebuilt binary for the build architecture, verifies it against the
upstream ``.sha256`` file in ``%prep``, and installs it with the same layout as
the parent spec. Consequences:

* No PAM authentication support (upstream binaries are built without the ``pam`` tag).
* No golang/nodejs needed at build time; builds are fast.
* ``GITEA_CUSTOM=/etc/gitea`` is set in the systemd unit so the service finds custom
  templates and options where the parent's compiled-in path put them.

Supported architectures: ``x86_64`` (amd64) and ``aarch64`` (arm64). Every supported
architecture's binary is embedded in the SRPM, because Copr/mock build the SRPM once
and rebuild each chroot offline. To add an architecture, add an ``%ifarch`` block
defining ``%goarch``, a ``SourceNN``/``SourceNN+1`` pair for the ``.xz`` binary and its
``.xz.sha256``, the matching ``cp`` line in ``%prep``, and the arch to ``ExclusiveArch``.

Builds are published from Copr `bennyfactor/gitea
<https://copr.fedorainfracloud.org/coprs/bennyfactor/gitea/>`_. To test-build locally
with podman (no mock needed)::

    scripts/container-build.sh el8          # full build into build/el8/
    scripts/container-build.sh el9 -bp      # %prep only on AlmaLinux 9

Upgrading from older packages of this fork
++++++++++++++++++++++++++++++++++++++++++

The 1.20.x/1.21.x packages from this fork ran without ``GITEA_CUSTOM``, so Gitea
used ``/var/lib/gitea/custom`` as its custom path. From 28.2.0-1 the unit sets
``GITEA_CUSTOM=/etc/gitea``. Before upgrading:

* **Back up** the database and ``/var/lib/gitea``. The package restarts the service
  after upgrade and Gitea runs its database migrations on first start.
* Move anything under ``/var/lib/gitea/custom/`` (templates, ``public/``, ``options/``,
  ``robots.txt``) to ``/etc/gitea/``.
* If ``CERT_FILE``/``KEY_FILE`` in ``app.ini`` are relative (the default
  ``https/cert.pem``), they now resolve under ``/etc/gitea``; make them absolute or move
  the files.
* To hold a host on the old version until you are ready, ``dnf versionlock add gitea``
  or add ``exclude=gitea`` to the Copr repo file.
