%ifarch x86_64
%bcond_without redfish
%bcond_without libsmbios
%endif

# although we ship a few tiny python files these are utilities that 99.99%
# of users do not need -- use this to avoid dragging python onto NestOS
%global __requires_exclude ^/usr/bin/python3

%ifarch x86_64 aarch64
%bcond_without uefi
%endif

Name:           fwupd
Version:        1.5.8
Release:        2
Summary:        Make updating firmware on Linux automatic, safe and reliable
License:        LGPLv2+
URL:            https://github.com/fwupd/fwupd/releases
Source0:        http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

BuildRequires:	gettext glib2-devel libxmlb-devel valgrind valgrind-devel libgcab1-devel
BuildRequires:  gpgme-devel libgudev1-devel libgusb-devel libsoup-devel polkit-devel sqlite-devel libxslt
BuildRequires:  gobject-introspection-devel libarchive-devel systemd gcab elfutils-libelf-devel
BuildRequires:  bash-completion json-glib-devel help2man vala meson gnutls-utils gnutls-devel gtk-doc
BuildRequires:  libjcat-devel tpm2-tss-devel

%if %{with uefi}
BuildRequires: python3 python3-cairo python3-gobject python3-pillow
BuildRequires: freetype fontconfig google-noto-sans-cjk-ttc-fonts
BuildRequires: gnu-efi-devel pesign efivar-devel pango-devel cairo-devel cairo-gobject-devel
%endif

%if %{with redfish}
BuildRequires: efivar-devel
%endif

%if %{with libsmbios}
BuildRequires: efivar-devel libsmbios-devel
%endif

Requires:      glib2 bubblewrap libsoup libgusb libxmlb shared-mime-info libjcat tpm2-tss
Requires(post):systemd
Requires(preun):systemd
Requires(postun):systemd

%description
%{name} aims to make updating firmware on Linux automatic, safe and reliable.

%package devel
Summary:       Development and installed test files for %{name}
Requires:      %{name} = %{version}-%{release} libjcat-devel
Provides:      %{name}-tests = %{version}-%{release}
Obsoletes:     %{name}-tests < %{version}-%{release}

%description devel
This package contains the development and installed test files for %{name}.

%package_help

%prep
%autosetup -n %{name}-%{version} -p1

%build
%meson -Dtests=true -Dgtkdoc=true -Dplugin_dummy=true \
%if %{with uefi}
       -Dplugin_nvme=true \
%else
       -Dplugin_nvme=false \
%endif
%if %{with redfish}
       -Dplugin_redfish=true \
%else
       -Dplugin_redfish=false \
%endif
%if %{with libsmbios}
       -Dplugin_dell=true \
%else
       -Dplugin_dell=false \
%endif
       -Dplugin_msr=false \
       -Dman=true

%meson_build

%install
%meson_install

%if %{with uefi}
%ifarch x86_64
%pesign -s -i %{buildroot}%{_libexecdir}/%{name}/efi/%{name}x64.efi -o %{buildroot}%{_libexecdir}/%{name}/efi/%{name}x64.efi.signed
%endif
%ifarch aarch64
%pesign -s -i %{buildroot}%{_libexecdir}/%{name}/efi/%{name}aa64.efi -o %{buildroot}%{_libexecdir}/%{name}/efi/%{name}aa64.efi.signed
%endif
%endif

mkdir -pm 0700 %{buildroot}%{_localstatedir}/lib/%{name}/gnupg

%find_lang %{name}

%check
%meson_test

%post
/sbin/ldconfig
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart %{name}.service
%systemd_postun_with_restart pesign.service

%files -f %{name}.lang
%doc README.md
%license COPYING AUTHORS
%{_bindir}/*
%config(noreplace)%{_sysconfdir}/%{name}/remotes.d/*.conf
%config(noreplace)%{_sysconfdir}/pki/%{name}
%config(noreplace)%{_sysconfdir}/%{name}/daemon.conf
%config(noreplace)%{_sysconfdir}/%{name}/thunderbolt.conf
%config(noreplace)%{_sysconfdir}/%{name}/uefi_capsule.conf
%config(noreplace)%{_sysconfdir}/%{name}/upower.conf
%{_sysconfdir}/pki/fwupd-metadata
%{_datadir}/dbus-1/system.d/*.%{name}.conf
%{_libexecdir}/%{name}/%{name}
%{_libexecdir}/%{name}/%{name}offline
%{_datadir}/bash-*/completions/*
%{_datadir}/metainfo/*.metainfo.xml
%{_datadir}/dbus-1/interfaces/*.fwupd.xml
%{_datadir}/dbus-1/system-services/*.service
%{_datadir}/polkit-1/*/org.freedesktop*
%{_datadir}/%{name}/
%{_datadir}/icons/hicolor/scalable/apps/*.%{name}.svg
%{_localstatedir}/lib/%{name}/*/*.md
%{_libdir}/lib%{name}*.so.*
%{_libdir}/girepository-1.0/*.typelib
%{_unitdir}/*.service
%{_unitdir}/*.wants/
%{_libdir}/fwupd-plugins-3/*.so
%ghost %{_localstatedir}/lib/fwupd/gnupg
%if %{with uefi}
%{_libexecdir}/%{name}/efi/*.efi
%{_libexecdir}/%{name}/efi/*.efi.signed
%endif
%if %{with redfish}
%config(noreplace)%{_sysconfdir}/%{name}/redfish.conf
%endif
%{_presetdir}/fwupd-refresh.preset
/usr/lib/udev/rules.d/*.rules
/usr/lib/systemd/system-shutdown/fwupd.shutdown
%{_unitdir}/fwupd-refresh.timer
%ifarch x86_64
%{_libexecdir}/fwupd/fwupd-detect-cet
%endif
%{_datadir}/fish/vendor_completions.d/fwupdmgr.fish

%files devel
%{_libdir}/*.so
%{_libdir}/*/*.pc
%{_includedir}/*
%{_datadir}/vala/*
%{_datadir}/gtk-doc/*/%{name}
%{_datadir}/doc/%{name}
%{_datadir}/*/*.gir
%{_datadir}/installed-tests/%{name}
%{_libexecdir}/installed-tests/%{name}
%dir %{_sysconfdir}/%{name}/remotes.d
%config(noreplace)%{_sysconfdir}/%{name}/remotes.d/%{name}-tests.conf

%files help
%{_datadir}/man/man1/*

%changelog
* Mon Jun 20 2022 fushanqing <fushanqing@kylinos.cn> - 1.5.8-2
- Remove the python installation dependency of fwupd

* Mon Jun 17 2022 lin zhang <lin.zhang@turbolinux.com.cn> - 1.5.8-1
- Upgrade to 1.5.8

* Wed Jun 15 2022 xigaoxinyan <xigaoxinyan@h-partners.com> - 1.2.14-1
- Update to 1.2.14

* Sun Jun 28 2020 huanghaitao <huanghaitao@huawei.com> - 1.2.9-3
- Solve build problem with check

* Mon Dec 9 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.2.9-2
- Solve build problem of x86

* Wed Nov 20 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.2.9-1
- Package init
