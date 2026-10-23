# Upstream dropped the leading "1." after 1.27.x; 28.x follows 1.27.x.
%global major_version 28
%global minor_version 2
%global micro_version 0

# Upstream's GOARCH name for the build architecture. To support another arch,
# add an %%ifarch block here, a Source pair below, and the arch to ExclusiveArch.
%ifarch x86_64
%global goarch amd64
%endif
%ifarch aarch64
%global goarch arm64
%endif

%define debug_package %{nil}

Name:		gitea
Version:	%{major_version}.%{minor_version}.%{micro_version}
Release:	1%{?dist}
Summary:	A painless self-hosted Git service
License:	MIT
URL:		https://gitea.io
ExclusiveArch:	x86_64 aarch64

Source0:	https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-src-%{version}.tar.gz
#Source1:	https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-docs-%{version}.tar.gz
Source2:	gitea.service
Source3:  gitea.firewalld
Source4:  README.EL+Fedora
Source5:  gitea.httpd
Source6:  gitea.nginx
Source7:  gitea.caddy
Source8:  gitea.sysusers
Source9:  gitea.profile.sh
Source10:  gitea.profile.csh
# Upstream prebuilt binaries (xz-compressed) and their checksums, one pair per
# supported arch. All are embedded in the SRPM; %%prep picks the one for %%{_arch}.
Source20: https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-%{version}-linux-amd64.xz
Source21: https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-%{version}-linux-amd64.xz.sha256
Source22: https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-%{version}-linux-arm64.xz
Source23: https://github.com/go-gitea/gitea/releases/download/v%{version}/%{name}-%{version}-linux-arm64.xz.sha256

Patch1:		0001-gitea.app.ini.patch

BuildRequires:	systemd
BuildRequires:	xz
Requires:	git
Requires:	git >= 2.25.0
Requires:	systemd
Requires: openssh-server
Requires(pre):	shadow-utils
Requires(post):	systemd
Requires(postun):	systemd
Requires(preun):	systemd

Conflicts:	git-web

# Suggesting httpd for now
Suggests:	httpd

%description
A painless self-hosted Git service.

Gitea is a community managed fork of Gogs. A lightweight code hosting solution
written in Go and published under the MIT license.

%package httpd
Summary:  Apache (httpd) configuration for %{name}
Requires: gitea
Requires: httpd

%description httpd
This subpackage contains Apache configuration files that can be used to reverse
proxy for Gitea.

%package nginx
Summary: nginx configuration for %{name}
Requires: gitea
Requires: nginx

%description nginx
This subpackage contains an nginx configuration file that can be used to reverse
proxy for Gitea.

%package caddy
Summary: caddy configuration for %{name}
Requires: gitea
Requires: caddy >= 2.0.0

%description caddy
This subpackage contains an caddy configuration file that can be used to reverse
proxy for Gitea.

#package docs
#Summary: Documentation for %{name}

#%description docs
#This subpackage contains the Gitea documentation from https://docs.gitea.io

%prep
%setup -q -n %{name}-src-%{version}
%autopatch -p1

install -m 0644 %{SOURCE4} .

# Select, verify and unpack the upstream prebuilt binary for this arch
%ifarch x86_64
cp -p %{SOURCE20} %{SOURCE21} .
%endif
%ifarch aarch64
cp -p %{SOURCE22} %{SOURCE23} .
%endif
sha256sum -c %{name}-%{version}-linux-%{goarch}.xz.sha256
xz -d %{name}-%{version}-linux-%{goarch}.xz
mv %{name}-%{version}-linux-%{goarch} gitea
chmod 0755 gitea
for file in $(find . -type f -name "*.css"); do
  chmod -x ${file}
done
ls 

%build
# Nothing to build: the upstream prebuilt binary is unpacked in %%prep.

%install
install -D -m 755 gitea $RPM_BUILD_ROOT%{_bindir}/gitea
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT/%{_unitdir}/gitea.service
install -D -m 644 custom/conf/app.example.ini $RPM_BUILD_ROOT%{_sysconfdir}/gitea/conf/app.ini
install -D -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/%{name}.xml
install -D -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -D -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/%{name}.conf
install -D -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/caddy/Caddyfile.d/%{name}.caddyfile
install -D -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysusersdir}/%{name}.conf
mkdir -p $RPM_BUILD_ROOT%{_datadir}/gitea \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/lfs \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/tmp \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/tmp/uploads \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/tmp/pprof \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/sessions \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/avatars \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/attachments \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/data/repo-avatars \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/https \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/indexers \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/indexers/issues.bleve \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/indexers/issues.queue \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/indexers/repos.bleve \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/queues \
  $RPM_BUILD_ROOT%{_localstatedir}/lib/gitea/repositories \
  $RPM_BUILD_ROOT%{_localstatedir}/log/gitea \
  $RPM_BUILD_ROOT%{_sysconfdir}/gitea/{conf,https,mailer}

cp -r options $RPM_BUILD_ROOT%{_datadir}/gitea/
cp -r public $RPM_BUILD_ROOT%{_datadir}/gitea/
cp -r templates $RPM_BUILD_ROOT%{_datadir}/gitea/
#cp -r web_src/less $RPM_BUILD_ROOT%{_datadir}/gitea/public
#install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/docs.gitea.io/

mkdir -p $RPM_BUILD_ROOT%{_tmpfilesdir}/
cat > $RPM_BUILD_ROOT%{_tmpfilesdir}/%{name}.conf <<EOF
d /run/gitea 0755 git git -
EOF

install -D -m 644 %{SOURCE9} %{buildroot}%{_sysconfdir}/profile.d/gitea.sh
install -D -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/profile.d/gitea.csh

%pre
# Not official
%if 0%{?fedora} || 0%{?rhel} >= 9
%sysusers_create_compat %{SOURCE8}
%else
%{_sbindir}/groupadd -r git 2>/dev/null || :
%{_sbindir}/useradd -r -g git \
  -s /bin/bash -d %{_datadir}/%{name} \
  -c 'Gitea' git 2>/dev/null || :
%endif

%preun
%systemd_preun %{name}.service

%post
%systemd_post %{name}.service
systemd-tmpfiles --create %{name}.conf || :

%postun
%systemd_postun_with_restart %{name}.service

%files
%doc README.EL+Fedora README.md custom/conf/app.example.ini
%license LICENSE
#exclude %{_datadir}/%{name}/docs.gitea.io
%{_unitdir}/gitea.service
%{_bindir}/gitea
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_tmpfilesdir}/%{name}.conf
%{_sysusersdir}/%{name}.conf
# setting this as config as users may manipulate it
%config %{_sysconfdir}/profile.d/gitea.*sh

%defattr(0660,root,git,770)
%dir %{_sysconfdir}/gitea
%dir %{_sysconfdir}/gitea/conf
%dir %{_sysconfdir}/gitea/https
%dir %{_sysconfdir}/gitea/mailer
%dir %{_localstatedir}/log/gitea
%config(noreplace) %{_sysconfdir}/gitea/conf/app.ini

%defattr(0660,git,git,750)
%{_datadir}/gitea
%{_localstatedir}/lib/gitea

%files httpd
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf

%files nginx
%config(noreplace) %{_sysconfdir}/nginx/conf.d/%{name}.conf

%files caddy
%config(noreplace) %{_sysconfdir}/caddy/Caddyfile.d/%{name}.caddyfile

#files docs
#{_datadir}/%{name}/docs.gitea.io

%changelog
* Fri Oct 23 2026 Benjamin Lamb <bennyfactor@iaatb.net> - 28.2.0-1
- Update to 28.2.0 (upstream dropped the leading "1." after 1.27.x)
- Merge nazunalika/rpmspecs-gitea at 1.23.4 (docs subpackage dropped upstream,
  profile.d GITEA_CUSTOM, autopatch)
- Install upstream prebuilt binary for x86_64/aarch64, verified by sha256,
  instead of compiling (no PAM support in the prebuilt binary)
- Fix APP_DATA_PATH to /var/lib/gitea/data
- Set GITEA_CUSTOM=/etc/gitea in the systemd unit. UPGRADE NOTE: the custom path moves
  from /var/lib/gitea/custom to /etc/gitea; move any custom/ contents there and use
  absolute CERT_FILE/KEY_FILE paths. Back up before upgrading: the service restarts
  into the new version and runs database migrations.
- Require git >= 2.25.0

* Tue Feb 18 2025 Louis Abel <tucklesepk@gmail.com> - 1.23.4-1
- Update to 1.23.4

* Wed Feb 05 2025 Louis Abel <tucklesepk@gmail.com> - 1.23.2-1
- Update to 1.23.2

* Thu Jan 09 2025 Louis Abel <tucklesepk@gmail.com> - 1.23.0-1
- Update to 1.23.0

* Wed Dec 11 2024 Louis Abel <tucklesepk@gmail.com> - 1.22.5-1
- Update to 1.22.5

* Mon Nov 25 2024 Louis Abel <tucklesepk@gmail.com> - 1.22.4-1
- Update to 1.22.4

* Thu Nov 07 2024 Louis Abel <tucklesepk@gmail.com> - 1.22.3-1
- Update to 1.22.3

* Fri May 31 2024 Louis Abel <tucklesepk@gmail.com> - 1.22.0-1
- Update to 1.22.0

* Mon Apr 15 2024 Louis Abel <tucklesepk@gmail.com> - 1.21.11-1
- Update to 1.21.11

* Mon Feb 26 2024 Louis Abel <tucklesepk@gmail.com> - 1.21.7-1
- Update to 1.21.7

* Tue Jan 16 2024 Louis Abel <tucklesepk@gmail.com> - 1.21.4-1
- Update to 1.21.4

* Sat Jan 06 2024 Louis Abel <tucklesepk@gmail.com> - 1.21.3-2
- Change git user shell to /bin/bash

* Thu Dec 21 2023 Louis Abel <tucklesepk@gmail.com> - 1.21.3-1
- Update to 1.21.3

* Tue Dec 12 2023 Louis Abel <tucklesepk@gmail.com> - 1.21.2-1
- Update to 1.21.2

* Sun Nov 26 2023 Louis Abel <tucklesepk@gmail.com> - 1.21.1-1
- Update to 1.21.1

* Tue Nov 14 2023 Louis Abel <tucklesepk@gmail.com> - 1.21.0-1
- Update to 1.21.0

* Tue Oct 03 2023 Louis Abel <tucklesepk@gmail.com> - 1.20.5-1
- Update to 1.20.5

* Fri Sep 08 2023 Louis Abel <tucklesepk@gmail.com> - 1.20.4-1
- Update to 1.20.4

* Sun Aug 20 2023 Louis Abel <tucklesepk@gmail.com> - 1.20.3-1
- Update to 1.20.3

* Sat Jul 29 2023 Louis Abel <tucklesepk@gmail.com> - 1.20.2-1
- Update to 1.20.2

* Sat Jul 22 2023 Louis Abel <tucklesepk@gmail.com> - 1.20.1-1
- Update to 1.20.1

* Sun Jul 16 2023 Louis Abel <tucklesepk@gmail.com> - 1.20.0-1
- Update to 1.20.0
- Clear change log
