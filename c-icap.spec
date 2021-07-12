# vim: sw=4:ts=4:et

Name: c-icap-server
Version: 0.5.8
Release: 1%{dist}
Summary: ICAP server c-icap-server

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
Source0: https://downloads.sourceforge.net/%{name}/c_icap-%{version}.tar.gz
Source1: c-icap-server.logrotate
Source2: c-icap-server.service
Source3: c-icap-server.tmpfiles.conf
Source4: c-icap-server.env

Patch0: %{name}-%{version}.patch

BuildRequires: libtool, bzip2-devel, libdb-devel, libmemcached-devel, openldap-devel, pcre-devel, zlib-devel, doxygen
%if 0%{?fedora} >= 26
BuildRequires: compat-openssl10-devel
%else
BuildRequires: openssl-devel
%endif

%description
c-icap is an opensource implementation of an ICAP server.
It can be used with HTTP proxies that support the ICAP protocol to implement ICAP-style content adaptation and filtering services.

Most commercial HTTP proxies support the ICAP protocol (ie. squid 3.x+).


%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: openssl-devel
Requires: c-icap-libs >= %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing applications that use %{name}.


%prep
%setup -q -n c_icap-%{version}
find -name Makefile.am | xargs sed -i -e 's/-rdynamic -rpath @libdir@//'
%patch0 -p1

%build
autoreconf -f -i
%configure --disable-static
%make_build
%make_build doc

%install
%{__mkdir_p} %{buildroot}%{_sbindir}/ %{buildroot}%{_sysconfdir}/logrotate.d/ %{buildroot}%{_sysconfdir}/sysconfig/ %{buildroot}%{_sysconfdir}/c-icap %{buildroot}%{_var}/log/c-icap/
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
find %{buildroot} -name '*.la' -exec rm -f {} \;
## systemd stuff
%if 0%{usesystemd} > 0
%{__mkdir_p} %{buildroot}/lib/systemd/system/ %{buildroot}/usr/lib/tmpfiles.d %{buildroot}%{_mandir}/man8
install -m 644 %{SOURCE2} %{buildroot}/lib/systemd/system/
install -m 644 %{SOURCE3} %{buildroot}/usr/lib/tmpfiles.d/c-icap-server.conf
%endif
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'
mv %{buildroot}%{_bindir}/c-icap %{buildroot}%{_sbindir}/

%check
cd tests
DONE=0
for test in test_*; do
    if [ -x "$test" ] && [ "x$test" != "xtest_body" ] && [ "x$test" != "xtest_tables" ]; then
        ./$test
        [ "x$DONE" != "x0" ] && DONE="$?"
        echo ">> $test ==> done? $DONE"
    fi
done
exit "$DONE"

%pre
USER="c-icap"
GROUP="c-icap"
HOMEDIR="/opt/home/$USER"

# create group+service user
RC=1
getent group $GROUP >/dev/null 2>&1 && RC=0
if [ "x$RC" != "x0" ]; then
    groupadd $GROUP ||:
fi
RC=1
getent passwd $USER >/dev/null 2>&1 && RC=0
if [ "x$RC" != "x0" ]; then
    if [ ! -d "$HOMEDIR" ]; then
        mkdir -p "$HOMEDIR" ||:
    fi
    useradd -d "$HOMEDIR" -m -c "c-icap-server service account" -g $GROUP -s /sbin/nologin $USER ||:
    chown $USER "$HOMEDIR" ||:
    chmod 2775 "$HOMEDIR" ||:
fi

# prevent systemd from NOT handling the .service after ie. an upgrade.
RC=1
if [ -e "/lib/systemd/system/c-icap-server.service" ]; then
    service c-icap-server status >/dev/null 2>&1 && RC=0
    if [ "x$RC" == "x0" ]; then
        service c-icap-server stop >/dev/null 2>&1 ||:
        sleep 2
        pkill -9 /usr/bin/c-icap ||:
        sleep 1
        service c-icap-server stop >/dev/null 2>&1 ||:
    fi
fi

%preun
service c-icap-server stop >/dev/null 2>&1 ||:

%post
/sbin/ldconfig ||:
systemctl daemon-reload ||:
service c-icap-server restart >/dev/null 2>&1 ||:
/bin/systemd-tmpfiles --create ||:

%postun
/sbin/ldconfig ||:
systemctl daemon-reload ||:
/bin/systemd-tmpfiles --create ||:

%files
%license COPYING
%doc AUTHORS README TODO
%config(noreplace) %{_sysconfdir}/c-icap.conf
%config(noreplace) %{_sysconfdir}/c-icap.magic
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config %{_sysconfdir}/c-icap.conf.default
%config %{_sysconfdir}/c-icap.magic.default
%{_sbindir}/c-icap
%{_bindir}/c-icap-mkbdb
%{_bindir}/c-icap-stretch
%{_mandir}/man8/c-icap.8*
%{_mandir}/man8/c-icap-mkbdb.8*
%{_mandir}/man8/c-icap-stretch.8*
%{_sysconfdir}/logrotate.d/%{name}
%attr(2775, c-icap, c-icap) %{_var}/log/c-icap/
%ghost %{_var}/log/c-icap/c-icap_server.log
%ghost %{_var}/log/c-icap/c-icap_access.log
%ghost %{_var}/log/c-icap/c-icap_access-vscan.log
%if 0%{usesystemd} > 0
/lib/systemd/system/%{name}.service
/usr/lib/tmpfiles.d/%{name}.conf
%endif


%files devel
%doc docs/html
%{_bindir}/c-icap-config
%{_bindir}/c-icap-libicapapi-config
%{_includedir}/*
%{_libdir}/*.so
%{_mandir}/man8/c-icap-config.8*
%{_mandir}/man8/c-icap-libicapapi-config.8*


%package -n c-icap-libs
Summary: Libraries needed by c-icap-server and c-icap-client

%description -n c-icap-libs
These are the libraries needed by c-icap-server and c-icap-client.

%files -n c-icap-libs
%{_libdir}/*.so.5*
%{_libdir}/c_icap/


%package -n c-icap-client
Summary: Client software for c-icap-server
Requires: c-icap-libs >= %{version}-%{release}

%description -n c-icap-client
c-icap-client is the client implementation for c-icap-server.
It can be used for debugging or together with HTTP proxies that support the ICAP protocol to implement content adaptation and filtering services.

%files -n c-icap-client
%{_bindir}/c-icap-client
%{_mandir}/man8/c-icap-client.8*


%changelog
* Mon Jul 12 2021 Frederic Krueger <fkrueger-dev-cicap@holics.at> - 0.5.8-1
- Initial package

