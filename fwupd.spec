%global glib2_version 2.45.8
%global libxmlb_version 0.1.3
%global libgusb_version 0.3.5
%global libcurl_version 7.62.0
%global libjcat_version 0.1.0
%global systemd_version 231
%global json_glib_version 1.1.1

%global __requires_exclude ^%{python3}$
%global enable_tests 1

%global enable_dummy 1

# fwupd.efi is only available on these arches
%ifarch x86_64 aarch64
%global have_uefi 1
%endif

# gpio.h is only available on these arches
%ifarch x86_64 aarch64
%global have_gpio 1
%endif

# flashrom is only available on these arches
%ifarch i686 x86_64 armv7hl aarch64 ppc64le
%global have_flashrom 0
%endif

%ifarch i686 x86_64
%global have_msr 1
%endif

# libsmbios is only available on x86
%ifarch x86_64
%global have_dell 1
%endif

# Until we actually have seen it outside x86
%ifarch i686 x86_64
%global have_thunderbolt 1
%endif


Name:      fwupd
Version:   1.8.6
Release:   3
License:   LGPLv2+
Summary:   Make updating firmware on Linux automatic, safe and reliable
URL:       https://github.com/fwupd/fwupd
Source0:   https://github.com/fwupd/fwupd/archive/refs/tags/1.8.6.tar.gz
Source2:   http://people.freedesktop.org/~hughsient/releases/fwupd-efi-1.1.tar.xz
Source3:   centos-ca-secureboot.der
Source4:   centossecureboot001.der
Source5:   centossecurebootca2.der
Source6:   centossecureboot203.der
Source7:   http://people.redhat.com/rhughes/dbx/DBXUpdate-20100307-x64.cab
Source8:   http://people.redhat.com/rhughes/dbx/DBXUpdate-20140413-x64.cab
Source9:   http://people.redhat.com/rhughes/dbx/DBXUpdate-20160809-x64.cab
Source10:  http://people.redhat.com/rhughes/dbx/DBXUpdate-20200729-aa64.cab
Source11:  http://people.redhat.com/rhughes/dbx/DBXUpdate-20200729-ia32.cab
Source12:  http://people.redhat.com/rhughes/dbx/DBXUpdate-20200729-x64.cab

Patch0:    fwupd-efi.patch


BuildRequires: libcbor libcbor-devel
BuildRequires: efi-srpm-macros
BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: libxmlb-devel >= %{libxmlb_version}
BuildRequires: libgcab1-devel
BuildRequires: libgudev1-devel
BuildRequires: libgusb-devel >= %{libgusb_version}
BuildRequires: libcurl-devel >= %{libcurl_version}
BuildRequires: polkit-devel >= 0.103
BuildRequires: sqlite-devel
BuildRequires: gpgme-devel libjcat-devel >= %{libjcat_version}
BuildRequires: systemd >= %{systemd_version}
BuildRequires: systemd-devel
BuildRequires: libarchive-devel
BuildRequires: gobject-introspection-devel
BuildRequires: gcab  meson >= 0.61.0
BuildRequires: protobuf-c   protobuf-c-devel  tpm2-tss-devel
BuildRequires: valgrind
BuildRequires: valgrind-devel
BuildRequires: python3  ninja-build python3-jinja2 python3-toml  python
BuildRequires: gnutls-devel
BuildRequires: gnutls-utils
BuildRequires: help2man
BuildRequires: json-glib-devel >= %{json_glib_version}
BuildRequires: vala
BuildRequires: bash-completion
BuildRequires: git-core

%if 0%{?have_uefi}
BuildRequires: efivar-devel >= 33
BuildRequires: python3 python3-cairo python3-gobject
BuildRequires: pango-devel
BuildRequires: cairo-devel cairo-gobject-devel
BuildRequires: freetype
BuildRequires: fontconfig
BuildRequires: google-noto-sans-cjk-ttc-fonts
BuildRequires: gnu-efi-devel
BuildRequires: pesign
%endif

%if 0%{?have_dell}
BuildRequires: efivar-devel >= 33
BuildRequires: libsmbios-devel >= 2.3.0
%endif


Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libxmlb%{?_isa} >= %{libxmlb_version}
Requires: libgusb%{?_isa} >= %{libgusb_version}
Requires: shared-mime-info

Obsoletes: fwupd-sign < 0.1.6
Obsoletes: libebitdo < 0.7.5-3
Obsoletes: libdfu < 1.0.0
Obsoletes: fwupd-labels < 1.1.0-1

Obsoletes: dbxtool < 9
Provides: dbxtool

# optional, but a really good idea
Recommends: udisks2
Recommends: bluez
Recommends: jq

%if 0%{?have_flashrom}
Recommends: %{name}-plugin-flashrom
%endif
%if 0%{?have_uefi}
Recommends: %{name}-efi
Recommends: %{name}-plugin-uefi-capsule-data
%endif


%description
%{name} aims to make updating firmware on Linux automatic, safe and reliable.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: libebitdo-devel < 0.7.5-3
Obsoletes: libdfu-devel < 1.0.0

%description devel
This package contains the development and installed test files for %{name}.

%package        help
Summary:        Documents for fwupd
Buildarch:      noarch
Requires:       man info
Obsoletes:      dbxtool-help < 9
Provides:       dbxtool-help

%description help
Man pages and other related documents for fwupd.

%prep
%autosetup -p1

mkdir -p subprojects/fwupd-efi
tar xfs %{SOURCE2} -C subprojects/fwupd-efi --strip-components=1

sed -ri '1s=^#!/usr/bin/(env )?python3=#!%{__python3}=' \
        contrib/ci/*.py \
        contrib/firmware_packager/*.py \
        contrib/*.py \
        contrib/standalone-installer/assets/*.py \
        contrib/standalone-installer/*.py \
        plugins/dfu/contrib/*.py \
        plugins/uefi-capsule/make-images.py \
        po/test-deps



%build

%meson \
    -Ddocs=disabled \
%if 0%{?enable_tests}
    -Dtests=true \
%else
    -Dtests=false \
%endif
%if 0%{?enable_dummy}
    -Dplugin_dummy=true \
%else
    -Dplugin_dummy=false \
%endif
%if 0%{?have_flashrom}
    -Dplugin_flashrom=enabled \
%else
    -Dplugin_flashrom=disabled \
%endif
%if 0%{?have_msr}
    -Dplugin_msr=enabled \
%else
    -Dplugin_msr=disabled \
%endif
%if 0%{?have_gpio}
    -Dplugin_gpio=enabled \
%else
    -Dplugin_gpio=disabled \
%endif
%if 0%{?have_uefi}
    -Dplugin_uefi_capsule=true \
    -Dplugin_uefi_pk=false \
%ifarch x86_64
    -Dfwupd-efi:efi_sbat_distro_id="rhel" \
    -Dfwupd-efi:efi_sbat_distro_summary="Red Hat Enterprise Linux" \
    -Dfwupd-efi:efi_sbat_distro_pkgname="%{name}" \
    -Dfwupd-efi:efi_sbat_distro_version="%{version}" \
    -Dfwupd-efi:efi_sbat_distro_url="mail:secalert@redhat.com" \
    -Dfwupd-efi:efi-libdir="/usr/lib64" \
%endif
    -Dplugin_tpm=false \
%else
    -Dplugin_uefi_capsule=false \
    -Dplugin_uefi_pk=false \
    -Dplugin_tpm=false \
%endif
%if 0%{?have_dell}
    -Dplugin_dell=enabled \
%else
    -Dplugin_dell=disabled \
%endif
    -Dplugin_modem_manager=disabled \
    -Dman=true \
    -Dbluez=enabled \
    -Dplugin_powerd=disabled \
    -Dsupported_build=enabled

%meson_build

%if 0%{?enable_tests}
%check
%meson_test
%endif

%install
%meson_install


mkdir -p %{buildroot}/%{_datadir}/dbxtool
install %{SOURCE7} %{SOURCE8} %{SOURCE9} %{SOURCE10} %{SOURCE11} %{SOURCE12} %{buildroot}/%{_datadir}/dbxtool

# sign fwupd.efi loader
%ifarch x86_64
%global efiarch x64
%global fwup_efi_fn   %{buildroot}%{_libexecdir}/%{name}/efi/%{name}x64.efi
%pesign -s -i %{fwup_efi_fn} -o %{fwup_efi_fn}.tmp -a %{SOURCE3} -c %{SOURCE4} -n centossecureboot001
%pesign -s -i %{fwup_efi_fn}.tmp -o %{fwup_efi_fn}.signed -a %{SOURCE5} -c %{SOURCE6} -n centossecureboot203
rm -fv %{fwup_efi_fn}.tmp
%endif

mkdir -p --mode=0700 $RPM_BUILD_ROOT%{_localstatedir}/lib/fwupd/gnupg

# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1757948
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/fwupd

mkdir -p %{buildroot}%{_datadir}/doc
mkdir -p %{buildroot}%{_datadir}/doc/fwupd
cp -r libfwupd* %{buildroot}%{_datadir}/doc/
cp -r *openEuler-linux*/libfwupd* %{buildroot}%{_datadir}/doc/fwupd/

sed -i '/DynamicUser=yes/d' %{buildroot}/usr/lib/systemd/system/fwupd-refresh.service

%find_lang %{name}

%post
%systemd_post fwupd.service

# change vendor-installed remotes to use the default keyring type
for fn in /etc/fwupd/remotes.d/*.conf; do
    if grep -q "Keyring=gpg" "$fn"; then
        sed -i 's/Keyring=gpg/#Keyring=pkcs/g' "$fn";
    fi
done

%preun
%systemd_preun fwupd.service

%postun
%systemd_postun_with_restart fwupd.service

%files -f %{name}.lang
%doc README.md AUTHORS
%license COPYING
%config(noreplace)%{_sysconfdir}/fwupd/daemon.conf
%if 0%{?have_uefi}
%config(noreplace)%{_sysconfdir}/fwupd/uefi_capsule.conf
%endif
%config(noreplace)%{_sysconfdir}/fwupd/redfish.conf
%if 0%{?have_thunderbolt}
%config(noreplace)%{_sysconfdir}/fwupd/thunderbolt.conf
%endif
%dir %{_libexecdir}/fwupd
%{_libexecdir}/fwupd/fwupd
%ifarch i686 x86_64
%{_libexecdir}/fwupd/fwupd-detect-cet
%endif
%{_libexecdir}/fwupd/fwupdoffline
%if 0%{?have_uefi}
%{_bindir}/fwupdate
%endif
%{_bindir}/dfu-tool
%if 0%{?have_uefi}
%{_bindir}/dbxtool
%endif
%{_bindir}/fwupdmgr
%{_bindir}/fwupdtool
%{_bindir}/fwupdagent
%dir %{_sysconfdir}/fwupd
%dir %{_sysconfdir}/fwupd/bios-settings.d
%config%(noreplace)%{_sysconfdir}/fwupd/bios-settings.d/README.md
%dir %{_sysconfdir}/fwupd/remotes.d
%if 0%{?have_dell}
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/dell-esrt.conf
%endif
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs-testing.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/vendor.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/vendor-directory.conf
%config(noreplace)%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/pki/fwupd-metadata
%if 0%{?have_msr}
/usr/lib/modules-load.d/fwupd-msr.conf
%config(noreplace)%{_sysconfdir}/fwupd/msr.conf
%endif
%{_datadir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/bash-completion/completions/fwupdmgr
%{_datadir}/bash-completion/completions/fwupdtool
%{_datadir}/bash-completion/completions/fwupdagent
%{_datadir}/fish/vendor_completions.d/fwupdmgr.fish
%{_datadir}/fwupd/metainfo/org.freedesktop.fwupd*.metainfo.xml
%if 0%{?have_dell}
%{_datadir}/fwupd/remotes.d/dell-esrt/metadata.xml
%endif
%{_datadir}/fwupd/remotes.d/vendor/firmware/README.md
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_datadir}/metainfo/org.freedesktop.fwupd.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/org.freedesktop.fwupd.svg
%{_datadir}/fwupd/firmware_packager.py
%{_datadir}/fwupd/simple_client.py
%{_datadir}/fwupd/add_capsule_header.py
%{_datadir}/fwupd/install_dell_bios_exe.py
%{_unitdir}/fwupd-offline-update.service
%{_unitdir}/fwupd.service
%{_unitdir}/fwupd-refresh.service
%{_unitdir}/fwupd-refresh.timer
%{_presetdir}/fwupd-refresh.preset
%{_unitdir}/system-update.target.wants/
%dir %{_localstatedir}/lib/fwupd
%dir %{_localstatedir}/cache/fwupd
%dir %{_datadir}/fwupd/quirks.d
%{_datadir}/fwupd/quirks.d/builtin.quirk.gz
%if 0%{?have_uefi}
%{_sysconfdir}/grub.d/35_fwupd
%endif
%{_libdir}/libfwupd.so.2*
%{_libdir}/girepository-1.0/Fwupd-2.0.typelib
/usr/lib/udev/rules.d/*.rules
/usr/lib/systemd/system-shutdown/fwupd.shutdown
%dir %{_libdir}/fwupd-%{version}
%{_libdir}/fwupd-%{version}/libfwupd*.so
%ghost %{_localstatedir}/lib/fwupd/gnupg

%if 0%{?have_flashrom}
%files plugin-flashrom
%{_libdir}/fwupd-%{version}/libfu_plugin_flashrom.so
%endif
%if 0%{?have_uefi}
%{_datadir}/fwupd/uefi-capsule-ux.tar.xz
%{_libexecdir}/%{name}/efi/*.efi
%ifarch x86_64
%{_libexecdir}/%{name}/efi/*.efi.signed
%endif
%endif
%dir %{_datadir}/dbxtool
%{_datadir}/dbxtool/DBXUpdate-20100307-x64.cab
%{_datadir}/dbxtool/DBXUpdate-20140413-x64.cab
%{_datadir}/dbxtool/DBXUpdate-20160809-x64.cab
%{_datadir}/dbxtool/DBXUpdate-20200729-aa64.cab
%{_datadir}/dbxtool/DBXUpdate-20200729-ia32.cab
%{_datadir}/dbxtool/DBXUpdate-20200729-x64.cab


%files devel
%{_datadir}/gir-1.0/Fwupd-2.0.gir
%{_datadir}/doc/fwupd/libfwupdplugin
%{_datadir}/doc/fwupd/libfwupd
%{_datadir}/doc/libfwupdplugin
%{_datadir}/doc/libfwupd
%{_datadir}/vala/vapi
%{_includedir}/fwupd-1
%{_libdir}/libfwupd*.so
%{_libdir}/pkgconfig/fwupd.pc
%{_libdir}/pkgconfig/fwupd-efi.pc
%if 0%{?enable_tests}
%{_datadir}/fwupd/host-emulate.d/*.json.gz
%dir %{_datadir}/installed-tests/fwupd
%{_datadir}/installed-tests/fwupd/tests/*
%{_datadir}/installed-tests/fwupd/fwupd-tests.xml
%{_datadir}/installed-tests/fwupd/*.test
%{_datadir}/installed-tests/fwupd/*.cab
%{_datadir}/installed-tests/fwupd/*.sh
%if 0%{?have_uefi}
%{_datadir}/installed-tests/fwupd/efi
%endif
%{_datadir}/fwupd/device-tests/*.json
%{_libexecdir}/installed-tests/fwupd/*
%{_datadir}/fwupd/__pycache__/*
%dir %{_sysconfdir}/fwupd/remotes.d
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/fwupd-tests.conf
%endif


%files help
%{_datadir}/man/man1/*

%changelog
* Thu Mar 02 2023 yaoxin <yaoxin30@h-partners.com> - 1.8.6-3
- Fix fwupd-refresh.service start failure

* Mon Feb 27 2023 liyanan <liyanan32@-partners.com> - 1.8.6-2
- Fix fwupd libjcat dbxtool file conflicts

* Tue Nov 1 2022 huyab<1229981468@qq.com> - 1.8.6-1
- update version to 1.8.6-1

* Thu Dec 01 2022 yaoxin <yaoxin30@h-partners.com> - 1.5.8-5
- Resolve fwupd upgrade and downgrade error

* Thu Dec 01 2022 Ge Wang <wangge20@h-partners.com> - 1.5.8-4
- Fix fwupd-refresh service start failure

* Thu Nov 10 2022 caodongxia <caodongxia@h-partners.com> - 1.5.8-3
- Fix compiling with new versions of efivar

* Mon Jun 20 2022 fushanqing <fushanqing@kylinos.cn> - 1.5.8-2
- Remove the python installation dependency of fwupd

* Mon Jun 17 2022 lin zhang <lin.zhang@turbolinux.com.cn> - 1.5.8-1
- Upgrade to 1.5.8

* Thu May 28 2015 Richard Hughes <richard@hughsie.com> 0.1.3-1
- New upstream release
- Coldplug the devices before acquiring the well known name
- Run the offline actions using systemd when required
- Support OpenHardware devices using the fwupd vendor extensions

* Wed Apr 22 2015 Richard Hughes <richard@hughsie.com> 0.1.2-1
- New upstream release
- Only allow signed firmware to be upgraded without a password

* Mon Mar 23 2015 Richard Hughes <richard@hughsie.com> 0.1.1-1
- New upstream release
- Add a 'get-updates' command to fwupdmgr
- Add and document the offline-update lifecycle
- Create a libfwupd shared library
- Create runtime directories if they do not exist
- Do not crash when there are no devices to return

* Mon Mar 16 2015 Richard Hughes <richard@hughsie.com> 0.1.0-1
- First release

