# vim: sw=4:ts=4:et

Name: c-icap-modules
Version: 0.5.5
Release: 1%{dist}
Summary: Modules for c-icap-server

%if 0%{?fedora} >= 14
%define usesystemd 1
%endif
%if "%{dist}" == ".el7"
%define usesystemd 1
%endif
%if "%{dist}" == ".el8"
%define usesystemd 1
%endif

License: LGPLv2+
URL: http://c-icap.sourceforge.net/
Source0: https://downloads.sourceforge.net/project/c-icap/c_icap_modules-%{version}.tar.gz

BuildRequires: clamav-devel, c-icap-server-devel, c-icap-server, c-icap-libs, zlib-devel, automake, autoconf
Requires: c-icap-server


%description
Official modules for the c-icap ICAP server.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: openssl-devel
Requires: c-icap-libs >= %{version}-%{release}
Patch0: %{name}-%{version}.patch

%description devel
The %{name}-devel package contains libraries and header files for developing applications that use %{name}.


%prep
%setup -q -n c_icap_modules-%{version}
%patch0 -p1


%build
%configure  CFLAGS="${RPM_OPT_FLAGS} -fno-strict-aliasing" --enable-shared --enable-static --with-bdb
make %{?_smp_mflags}


%install
%{__mkdir_p} %{buildroot}%{_sysconfdir}/c-icap/
%make_install DESTDIR=%{buildroot}
mv %{buildroot}%{_sysconfdir}/*.{conf,default} %{buildroot}%{_sysconfdir}/c-icap/

# cleanup
rm -f %{buildroot}%{_libdir}/c_icap/*.*a %{buildroot}%{_libdir}/*.*a
rm -f %{buildroot}%{_libdir}%{_bindir}/c-icap-mods-sguardDB-%{version}-%{release}.%{arch}.debug ||:


%post
/sbin/ldconfig ||:
service c-icap-modules restart >/dev/null 2>&1 ||:


%files
%license COPYING
%doc AUTHORS
%dir %{_libdir}/c_icap
%attr(0755,root,root) %{_libdir}/c_icap/*.so
%config(noreplace) %{_sysconfdir}/c-icap/clamav_mod.conf
%config(noreplace) %{_sysconfdir}/c-icap/clamd_mod.conf
%config(noreplace) %{_sysconfdir}/c-icap/srv_url_check.conf
%config(noreplace) %{_sysconfdir}/c-icap/virus_scan.conf
%config %{_sysconfdir}/c-icap/clamav_mod.conf.default
%config %{_sysconfdir}/c-icap/clamd_mod.conf.default
%config %{_sysconfdir}/c-icap/srv_content_filtering.conf.default
%config %{_sysconfdir}/c-icap/srv_url_check.conf.default
%config %{_sysconfdir}/c-icap/virus_scan.conf.default
%{_datadir}/c_icap/templates/srv_content_filtering/en/*
%{_datadir}/c_icap/templates/srv_url_check/en/*
%{_datadir}/c_icap/templates/virus_scan/en/*
%{_bindir}/c-icap-mods-sguardDB
%{_mandir}/man8/c-icap-mods-sguardDB.8*

%changelog
* Mon Jul 12 2021 Frederic Krueger <fkrueger-dev-cicap@holics.at> - 0.5.5-1
- Initial package

