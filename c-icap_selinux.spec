# vim: sw=4:ts=4:et

Name: c-icap-server_selinux
Version: 0.5.8
Release: 5%{dist}
Summary: SELinux policy module for c-icap-server

%define selinux_policyver 3.14.3-1
%define selinux_ppname cicap
%define selinux_porttype cicap_port_t
%define selinux_ports_tcp 1344
%define selinux_ports_udp %{nil}
%define selinux_dirs /etc/ /run/ /tmp/ /usr/ /var/log/ /var/run/ /var/tmp/

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
Source0: c-icap-server_selinux.te
Source1: c-icap-server_selinux.fc
Source2: c-icap-server_selinux.if
Source3: c-icap-server_selinux-readme.md

BuildRequires: libtool, bzip2-devel, libdb-devel, openldap-devel, pcre-devel, zlib-devel, doxygen, libmemcached

%description
This package installs and sets up the SELinux policy module for the c-icap-server package.

Requires: policycoreutils, libselinux-utils
Requires(post): selinux-policy-base >= %{selinux_policyver}, policycoreutils
Requires(postun): policycoreutils
BuildArch: noarch


%prep
TMPB="%{_builddir}/%{name}-%{version}-%{release}.%{_arch}/"
mkdir -p "$TMPB"
cp %{SOURCE0} "$TMPB/%{selinux_ppname}.te"
cp %{SOURCE1} "$TMPB/%{selinux_ppname}.fc"
cp %{SOURCE2} "$TMPB/%{selinux_ppname}.if"
cd "$TMPB"
make -f /usr/share/selinux/devel/Makefile

%install
%{__mkdir_p} %{buildroot}%{_datadir}/selinux/devel/include/contrib %{buildroot}%{_datadir}/selinux/packages/ %{buildroot}%{_defaultdocdir}/%{name}-%{version}/
install -m 644 %{_builddir}/%{name}-%{version}-%{release}.%{_arch}/%{selinux_ppname}.pp %{buildroot}%{_datadir}/selinux/packages
install -m 644 %{_builddir}/%{name}-%{version}-%{release}.%{_arch}/%{selinux_ppname}.if %{buildroot}%{_datadir}/selinux/devel/include/contrib
install -m 644 %{SOURCE3} %{buildroot}%{_defaultdocdir}/%{name}-%{version}/readme.md

%post
[ "x$1" == "x1" ] && FIRSTINSTALL="1"
# install policy modules
## generic part
semodule -n -i %{_datadir}/selinux/packages/%{selinux_ppname}.pp
for i in %{selinux_ports_tcp} XXX; do
    [ "x$i" != "xXXX" ] && semanage port -a -t %{selinux_porttype} -p tcp $i ||:
done
for i in %{selinux_ports_udp} XXX; do
    [ "x$i" != "xXXX" ] && semanage port -a -t %{selinux_porttype} -p udp $i ||:
done
## custom part
# setup
if /usr/sbin/selinuxenabled ; then
    /usr/sbin/load_policy
    restorecon -R %{selinux_dirs} ||:
fi
# XXX make sure c-icap is started with the new selinux context, but only during firstinstall.
if [ "x$FIRSTINSTALL" == "x1" ]; then
  echo "-> ONLY during first install: Stopping /usr/bin/c-icap and /usr/sbin/c-icap, then starting via service script."
  echo "--> Make sure it's still running after installation is finished!"
  echo ""
  service c-icap-server stop >/dev/null 2>&1 ||:
  sleep 2
  # XXX the following doesn't care where c-icap resides, be it in the default /usr/bin/c-icap oder our /usr/sbin/c-icap (since it's a daemon)
  pkill -9 c-icap >/dev/null 2>&1 ||:
  sleep 1
%if 0%{usesystemd} > 0
  # Only start c-icap-server if enabled in systemd
  systemctl is-enabled c-icap-server.service >/dev/null 2>&1 ||:
  if [ "x$?" == "x0" ]; then
    service c-icap-server start >/dev/null 2>&1 ||:
  fi
%endif
fi
exit 0


%postun
if [ $1 -eq 0 ]; then
    # try to remove all port definitions and context-mirroring.
    ## generic part
    for i in %{selinux_ports_tcp} XXX; do
        [ "x$i" != "xXXX" ] && semanage port -d -t %{selinux_porttype} -p tcp $i ||:
    done
    for i in %{selinux_ports_udp} XXX; do
        [ "x$i" != "xXXX" ] && semanage port -d -t %{selinux_porttype} -p udp $i ||:
    done
    ## custom part
    # then try to remove the policy module
    semodule -n -r %{selinux_ppname}
    if /usr/sbin/selinuxenabled ; then
       /usr/sbin/load_policy
       restorecon -R %{selinux_dirs} ||:
    fi;
fi;
exit 0


%files
%attr(0600,root,root) %{_datadir}/selinux/packages/%{selinux_ppname}.pp
%{_datadir}/selinux/devel/include/contrib/%{selinux_ppname}.if
%doc %{_defaultdocdir}/%{name}-%{version}/readme.md

%changelog
* Wed Feb 15 2023 Frederic Krueger <fkrueger-dev-cicap@holics.at> 0.5.8-5
- updated policy for newly added weirdness around rpm_script_t

* Tue Aug 31 2021 Frederic Krueger <fkrueger-dev-cicap@holics.at> 0.5.8-4
- added system_cronjob_t support

* Tue Aug 10 2021 Frederic Krueger <fkrueger-dev-cicap@holics.at> - 0.5.8-3
- added systemd_tmpfiles_t getattr/search dirs

* Sat Jul 17 2021 Frederic Krueger <fkrueger-dev-cicap@holics.at> - 0.5.8-2
- Removed needless dependencies

* Mon Jul 12 2021 Frederic Krueger <fkrueger-dev-cicap@holics.at> - 0.5.8-1
- Initial package

