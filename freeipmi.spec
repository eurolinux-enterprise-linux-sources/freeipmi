%global _hardened_build 1
# Copyright (c) 2003 FreeIPMI Core Team

Name:             freeipmi
Version:          1.5.7
Release:          2%{?dist}
Summary:          IPMI remote console and system management software
License:          GPLv3+
Group:            Applications/System
URL:              http://www.gnu.org/software/freeipmi/
Source0:          http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.gz
Source1:          bmc-watchdog.service
Source2:          ipmidetectd.service
Source3:          ipmiseld.service
Source4:          os-shutdown-event.service
Source5:          os-startup-event.service

Patch1:           freeipmi-1.5.7-manpage.patch

BuildRequires:    libgcrypt-devel texinfo systemd
Requires(preun):  info systemd
Requires(post):   info systemd systemd-sysv
Requires(postun): systemd

%description
The FreeIPMI project provides "Remote-Console" (out-of-band) and
"System Management Software" (in-band) based on Intelligent
Platform Management Interface specification.

%package devel
Summary:          Development package for FreeIPMI
Group:            Development/System
Requires:         %{name} = %{version}-%{release}
Requires:         OpenIPMI-modalias
%description devel
Development package for FreeIPMI.  This package includes the FreeIPMI
header files and libraries.

%package bmc-watchdog
Summary:          IPMI BMC watchdog
Group:            Applications/System
Requires:         %{name} = %{version}-%{release}
%description bmc-watchdog
Provides a watchdog daemon for OS monitoring and recovery.

%package ipmidetectd
Summary:          IPMI node detection monitoring daemon
Group:            Applications/System
Requires:         %{name} = %{version}-%{release}
%description ipmidetectd
Provides a tool and a daemon for IPMI node detection.

%package ipmiseld
Summary:          IPMI SEL syslog logging daemon
Group:            Applications/System
Requires:         %{name} = %{version}-%{release}
%description ipmiseld
IPMI SEL syslog logging daemon.

%if %{?_with_debug:1}%{!?_with_debug:0}
  %global _enable_debug --enable-debug --enable-trace --enable-syslog
%endif

%prep
%setup -q
%patch1 -p1 -b .manpage

%build
export CFLAGS="-D_GNU_SOURCE $RPM_OPT_FLAGS"
%configure --program-prefix=%{?_program_prefix:%{_program_prefix}} \
           %{?_enable_debug} --disable-static
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR="$RPM_BUILD_ROOT"
rm -rf $RPM_BUILD_ROOT%{_infodir}/dir
# kludge to get around rpmlint complaining about 0 length semephore file
echo freeipmi > $RPM_BUILD_ROOT%{_localstatedir}/lib/freeipmi/ipckey
# Remove .la files
rm -rf $RPM_BUILD_ROOT/%{_libdir}/*.la
# Install systemd units
install -m 755 -d $RPM_BUILD_ROOT/%{_unitdir}
install -m 644 %SOURCE1 %SOURCE2 %SOURCE3 %SOURCE4 %SOURCE5 $RPM_BUILD_ROOT/%{_unitdir}/
# Remove initscripts
rm -rf $RPM_BUILD_ROOT/%{_initrddir} $RPM_BUILD_ROOT/%{_sysconfdir}/init.d

%post
/sbin/install-info %{_infodir}/freeipmi-faq.info.gz %{_infodir}/dir &>/dev/null || :
/sbin/ldconfig
%systemd_post os-shutdown-event.service os-startup-event.service

%preun
if [ $1 = 0 ]; then
    /sbin/install-info --delete %{_infodir}/freeipmi-faq.info.gz %{_infodir}/dir &>/dev/null || :
fi
%systemd_preun os-shutdown-event.service os-startup-event.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart os-shutdown-event.service os-startup-event.service

%post bmc-watchdog
%systemd_post bmc-watchdog.service

%preun bmc-watchdog
%systemd_preun bmc-watchdog.service

%postun bmc-watchdog
%systemd_postun_with_restart bmc-watchdog.service

%post ipmiseld
%systemd_post ipmiseld.service

%preun ipmiseld
%systemd_preun ipmiseld.service

%postun ipmiseld
%systemd_postun_with_restart ipmiseld.service

%post ipmidetectd
%systemd_post ipmidetectd.service

%preun ipmidetectd
%systemd_preun ipmidetectd.service

%postun ipmidetectd
%systemd_postun_with_restart ipmidetectd.service

%triggerun -- freeipmi-bmc-watchdog < 1.1.1-2
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save bmc-watchdog >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del bmc-watchdog >/dev/null 2>&1 || :
/bin/systemctl try-restart bmc-watchdog.service >/dev/null 2>&1 || :

%triggerun -- freeipmi-ipmidetectd < 1.1.1-2
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save ipmidetectd >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del ipmidetectd >/dev/null 2>&1 || :
/bin/systemctl try-restart ipmidetectd.service >/dev/null 2>&1 || :

%files
%dir %{_sysconfdir}/freeipmi/
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmidetect.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi_interpret_sel.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/freeipmi_interpret_sensor.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/libipmiconsole.conf
%doc %{_datadir}/doc/%{name}/AUTHORS
%doc %{_datadir}/doc/%{name}/COPYING
%doc %{_datadir}/doc/%{name}/ChangeLog
%doc %{_datadir}/doc/%{name}/ChangeLog.0
%doc %{_datadir}/doc/%{name}/INSTALL
%doc %{_datadir}/doc/%{name}/NEWS
%doc %{_datadir}/doc/%{name}/README
%doc %{_datadir}/doc/%{name}/README.argp
%doc %{_datadir}/doc/%{name}/README.build
%doc %{_datadir}/doc/%{name}/README.openipmi
%doc %{_datadir}/doc/%{name}/TODO
%doc %{_infodir}/*
%doc %{_datadir}/doc/%{name}/COPYING.ipmiping
%doc %{_datadir}/doc/%{name}/COPYING.ipmipower
%doc %{_datadir}/doc/%{name}/COPYING.ipmiconsole
%doc %{_datadir}/doc/%{name}/COPYING.ipmimonitoring
%doc %{_datadir}/doc/%{name}/COPYING.pstdout
%doc %{_datadir}/doc/%{name}/COPYING.ipmidetect
%doc %{_datadir}/doc/%{name}/COPYING.ipmi-fru
%doc %{_datadir}/doc/%{name}/COPYING.ipmi-dcmi
%doc %{_datadir}/doc/%{name}/COPYING.sunbmc
%doc %{_datadir}/doc/%{name}/COPYING.ZRESEARCH
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiping
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmipower
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiconsole
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmimonitoring
%doc %{_datadir}/doc/%{name}/DISCLAIMER.pstdout
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmidetect
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-fru
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-dcmi
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiping.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmipower.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiconsole.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmimonitoring.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.pstdout.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmidetect.UC
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmi-fru.UC
%doc %{_datadir}/doc/%{name}/freeipmi-coding.txt
%doc %{_datadir}/doc/%{name}/freeipmi-design.txt
%doc %{_datadir}/doc/%{name}/freeipmi-hostrange.txt
%doc %{_datadir}/doc/%{name}/freeipmi-libraries.txt
%doc %{_datadir}/doc/%{name}/freeipmi-bugs-issues-and-workarounds.txt
%doc %{_datadir}/doc/%{name}/freeipmi-testing.txt
%doc %{_datadir}/doc/%{name}/freeipmi-oem-documentation-requirements.txt
%dir %{_datadir}/doc/%{name}
%dir %{_datadir}/doc/%{name}/contrib
%dir %{_datadir}/doc/%{name}/contrib/ganglia
%doc %{_datadir}/doc/%{name}/contrib/ganglia/*
%dir %{_datadir}/doc/%{name}/contrib/nagios
%doc %{_datadir}/doc/%{name}/contrib/nagios/*
%dir %{_datadir}/doc/%{name}/contrib/pet
%doc %{_datadir}/doc/%{name}/contrib/pet/*
%{_libdir}/libipmiconsole*so.*
%{_libdir}/libfreeipmi*so.*
%{_libdir}/libipmidetect*so.*
%{_libdir}/libipmimonitoring.so.*
%{_localstatedir}/lib/*
%{_sbindir}/bmc-config
%{_sbindir}/bmc-info
%{_sbindir}/bmc-device
%{_sbindir}/ipmi-config
%{_sbindir}/ipmi-fru
%{_sbindir}/ipmi-locate
%{_sbindir}/ipmi-oem
%{_sbindir}/ipmi-pef-config
%{_sbindir}/pef-config
%{_sbindir}/ipmi-raw
%{_sbindir}/ipmi-sel
%{_sbindir}/ipmi-sensors
%{_sbindir}/ipmi-sensors-config
%{_sbindir}/ipmiping
%{_sbindir}/ipmi-ping
%{_sbindir}/ipmipower
%{_sbindir}/ipmi-power
%{_sbindir}/rmcpping
%{_sbindir}/rmcp-ping
%{_sbindir}/ipmiconsole
%{_sbindir}/ipmi-console
%{_sbindir}/ipmimonitoring
%{_sbindir}/ipmi-chassis
%{_sbindir}/ipmi-chassis-config
%{_sbindir}/ipmi-dcmi
%{_sbindir}/ipmi-pet
%{_sbindir}/ipmidetect
%{_sbindir}/ipmi-detect
%{_mandir}/man8/bmc-config.8*
%{_mandir}/man5/bmc-config.conf.5*
%{_mandir}/man8/bmc-info.8*
%{_mandir}/man8/bmc-device.8*
%{_mandir}/man8/ipmi-config.8*
%{_mandir}/man5/ipmi-config.conf.5*
%{_mandir}/man8/ipmi-fru.8*
%{_mandir}/man8/ipmi-locate.8*
%{_mandir}/man8/ipmi-oem.8*
%{_mandir}/man8/ipmi-pef-config.8*
%{_mandir}/man8/pef-config.8*
%{_mandir}/man8/ipmi-raw.8*
%{_mandir}/man8/ipmi-sel.8*
%{_mandir}/man8/ipmi-sensors.8*
%{_mandir}/man8/ipmi-sensors-config.8*
%{_mandir}/man8/ipmiping.8*
%{_mandir}/man8/ipmi-ping.8*
%{_mandir}/man8/ipmipower.8*
%{_mandir}/man8/ipmi-power.8*
%{_mandir}/man5/ipmipower.conf.5*
%{_mandir}/man8/rmcpping.8*
%{_mandir}/man8/rmcp-ping.8*
%{_mandir}/man8/ipmiconsole.8*
%{_mandir}/man8/ipmi-console.8*
%{_mandir}/man5/ipmiconsole.conf.5*
%{_mandir}/man8/ipmimonitoring.8*
%{_mandir}/man5/ipmi_monitoring_sensors.conf.5*
%{_mandir}/man5/ipmimonitoring_sensors.conf.5*
%{_mandir}/man5/ipmimonitoring.conf.5*
%{_mandir}/man5/freeipmi_interpret_sel.conf.5*
%{_mandir}/man5/freeipmi_interpret_sensor.conf.5*
%{_mandir}/man5/libipmimonitoring.conf.5*
%{_mandir}/man8/ipmi-chassis.8*
%{_mandir}/man8/ipmi-chassis-config.8*
%{_mandir}/man8/ipmi-dcmi.8*
%{_mandir}/man8/ipmi-pet.8*
%{_mandir}/man8/ipmidetect.8*
%{_mandir}/man8/ipmi-detect.8*
%{_mandir}/man5/freeipmi.conf.5*
%{_mandir}/man5/ipmidetect.conf.5*
%{_mandir}/man5/libipmiconsole.conf.5*
%{_mandir}/man7/freeipmi.7*
%dir %{_localstatedir}/cache/ipmimonitoringsdrcache
%{_unitdir}/os-shutdown-event.service
%{_unitdir}/os-startup-event.service

%files devel
%dir %{_datadir}/doc/%{name}/contrib/libipmimonitoring
%doc %{_datadir}/doc/%{name}/contrib/libipmimonitoring/*
%{_libdir}/libipmiconsole.so
%{_libdir}/libfreeipmi.so
%{_libdir}/libipmidetect.so
%{_libdir}/libipmimonitoring.so
%dir %{_includedir}/freeipmi
%dir %{_includedir}/freeipmi/api
%dir %{_includedir}/freeipmi/cmds
%dir %{_includedir}/freeipmi/debug
%dir %{_includedir}/freeipmi/driver
%dir %{_includedir}/freeipmi/fiid
%dir %{_includedir}/freeipmi/fru
%dir %{_includedir}/freeipmi/interface
%dir %{_includedir}/freeipmi/interpret
%dir %{_includedir}/freeipmi/locate
%dir %{_includedir}/freeipmi/payload
%dir %{_includedir}/freeipmi/record-format
%dir %{_includedir}/freeipmi/record-format/oem
%dir %{_includedir}/freeipmi/sdr
%dir %{_includedir}/freeipmi/sdr/oem
%dir %{_includedir}/freeipmi/sel
%dir %{_includedir}/freeipmi/sensor-read
%dir %{_includedir}/freeipmi/spec
%dir %{_includedir}/freeipmi/spec/oem
%dir %{_includedir}/freeipmi/templates
%dir %{_includedir}/freeipmi/templates/oem
%dir %{_includedir}/freeipmi/util
%{_includedir}/ipmiconsole.h
%{_includedir}/ipmidetect.h
%{_includedir}/ipmi_monitoring*.h
%{_includedir}/freeipmi/*.h
%{_includedir}/freeipmi/api/*.h
%{_includedir}/freeipmi/cmds/*.h
%{_includedir}/freeipmi/debug/*.h
%{_includedir}/freeipmi/driver/*.h
%{_includedir}/freeipmi/fiid/*.h
%{_includedir}/freeipmi/fru/*.h
%{_includedir}/freeipmi/interface/*.h
%{_includedir}/freeipmi/interpret/*.h
%{_includedir}/freeipmi/locate/*.h
%{_includedir}/freeipmi/payload/*.h
%{_includedir}/freeipmi/record-format/*.h
%{_includedir}/freeipmi/record-format/oem/*.h
%{_includedir}/freeipmi/sdr/*.h
%{_includedir}/freeipmi/sdr/oem/*.h
%{_includedir}/freeipmi/sel/*.h
%{_includedir}/freeipmi/sensor-read/*.h
%{_includedir}/freeipmi/spec/*.h
%{_includedir}/freeipmi/spec/oem/*.h
%{_includedir}/freeipmi/templates/*.h
%{_includedir}/freeipmi/templates/oem/*.h
%{_includedir}/freeipmi/util/*.h
%{_mandir}/man3/*
%{_libdir}/pkgconfig/*

%files bmc-watchdog
%doc %{_datadir}/doc/%{name}/COPYING.bmc-watchdog
%doc %{_datadir}/doc/%{name}/DISCLAIMER.bmc-watchdog
%doc %{_datadir}/doc/%{name}/DISCLAIMER.bmc-watchdog.UC
%config(noreplace) %{_sysconfdir}/sysconfig/bmc-watchdog
%{_sbindir}/bmc-watchdog
%{_mandir}/man8/bmc-watchdog.8*
%{_unitdir}/bmc-watchdog.service

%files ipmidetectd
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmidetectd.conf
%{_sbindir}/ipmidetectd
%{_mandir}/man5/ipmidetectd.conf.5*
%{_mandir}/man8/ipmidetectd.8*
%{_unitdir}/ipmidetectd.service

%files ipmiseld
%doc %{_datadir}/doc/%{name}/COPYING.ipmiseld
%doc %{_datadir}/doc/%{name}/DISCLAIMER.ipmiseld
%{_unitdir}/ipmiseld.service
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/freeipmi/ipmiseld.conf
%{_sbindir}/ipmiseld
%{_mandir}/man5/ipmiseld.conf.5*
%{_mandir}/man8/ipmiseld.8*
%dir %{_localstatedir}/cache/ipmiseld

%changelog
* Mon Nov 20 2017 Josef Ridky <jridky@redhat.com> - 1.5.7-2
- Additional fix of manpage command examples (#1353981)

* Tue Aug 29 2017 Josef Ridky <jridky@redhat.com> - 1.5.7-1
- Rebase to the latest upstream release 1.5.7 (#1435848)
- Fix manpage command examples (#1353981) in separate commit

* Tue Jun 28 2016 Boris Ranto <branto@redhat.com> - 1.2.9-8
- Package os event systemd services (#1122307)

* Mon Jul 06 2015 Ales Ledvinka <aledvink@redhat.com> - 1.2.9-7
- Big-Endian authentication fix. (#1189065)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.2.9-6
- Mass rebuild 2014-01-24

* Fri Jan 17 2014 Ales Ledvinka <aledvink@redhat.com> - 1.2.9-5
- Fix dependencies to pull ipmi modules. (#1052180)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.2.9-3
- Mass rebuild 2013-12-27

* Sun Jul 21 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.9-2
- Requires modalias package for module loading dependency.

* Fri Jul 19 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.9-1
- Updated to upstream freeipmi-1.2.9
 - Fix threshold output corner case in ipmi-sensors.
 - Fix invalid declaration in libipmimonitoring header.
 - Fix older compiler build problems.
 -
 - Fix portability build bug on ARM systems.
 - Add 'internal IPMI error' troubleshooting to manpages.
 - Fix bmc-info corner case on Bull 510 systems.

* Fri May 31 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.7-2
- Fix build on architectures where va_list is not pointer.

* Mon May 20 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.7-1
- Updated to freeipmi-1.2.7
 - Fix sensor output errors with OEM sensors.

* Fri May 17 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.6-2
 - spec update by Christopher Meng <rpm@cicku.me>
 - hardened build flags should include PIE also for bmc-watchdog.

* Fri May 03 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.6-1
- Updated to freeipmi-1.2.6
 - Support HP Proliant DL160 G8 OEM sensors.
 - Support Supermicro X9SCM-iiF OEM sensors and events.
 - Support output of temperature sampling period to ipmi-dcmi.
 - Clarify error message when SOL session cannot be stolen in
   ipmiconsole/libipmiconsole.
 - Fix dcmi rolling average time period output error
 - Fix ipmi-dcmi output errors with --get-dcmi-sensor-info.
 - Fix corner case in calculation of confidentiality pad length with
   AES-CBC-128 encryption.  Incorrect pad effects some vendor firmware
   implementations.
 - Send IPMI 2.0 packets differently than IPMI 1.5 packets, as the
   former does not require legacy pad data to be appended to payloads.
 - Fix Intel OEM SEL buffer overflow.
 - Fix out of trunk source build.
 - Support new ipmi_rmcpplus_sendto() and ipmi_rmcpplus_recvfrom()
   functions.
 - Support new HP Proliant DL160 G8 OEM sensor events.

* Thu Feb 28 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.5-1
- Updated to freeipmi-1.2.5:
 - Support Supermicro X9SPU-F-O OEM sensors and events.
 - Support Supermicro X9DRI-LN4F+ OEM intepretations (previously
   forgotten).

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 11 2013 Ales Ledvinka <aledvink@redhat.com> - 1.2.4-1
- Updated to freeipmi-1.2.4:
 - Support Supermicro X9DRI-LN4F+ OEM sensors and events.
 - Fix output corner case for "session-based" channels.
 - Fix ipmi-oem set-power-restore-delay corner case in time settings.
 - Fix ipmiseld memleak.
 - Fix libfreeipmi potential fd leak when generating random numbers.
 - Fix libfreeipmi error output bug in RMCP interface.
 - Fix several minor corner cases discovered by static code analysis.

* Thu Nov 15 2012 Ales Ledvinka <aledvink@redhat.com> - 1.2.3-1
- Updated to freeipmi-1.2.3:
 - In ipmi-oem, support new Dell Poweredge R720 OEM commands extensions,
   including:
  - get-nic-selection-failover
  - set-nic-selection-failover
  - power-monitoring-over-interval
  - power-monitoring-interval-range
  - get-last-post-code
 - In ipmi-oem, update active-lom-status for Dell Poweredge R720.
 - In ipmi-oem, support new Dell Poweredge R720 get-system-info option
   'cmc-info'.
 - In ipmi-oem, Dell get-system-info "slot-number" key changed to
   "blade-slot-info".  Legacy option still supported.
 - In ipmi-sel, support Dell Poweredge R720 OEM SEL extensions.
 - In all tools, support nochecksumcheck workaround option.
 - In all daemons (ipmiseld, ipmidetectd, bmc-watchdog), check for
   syscall errors during daemon setup.

 - In libfreeipmi, support Dell R720 OEM extension intepretations.
 - In libfreeipmi, libipmimonitoring, and libipmiconsole, support
   NO_CHECKSUM_CHECK workaround flag.
 - In libipmiconsole, IPMICONSOLE_DEBUG_FILE logs debug to files in
   current working directory and not /var/log.  PID is also appended to
   debug files.

* Fri Oct 12 2012 Ales Ledvinka <aledvink@redhat.com> - 1.2.2-1
- Updated to freeipmi-1.2.2:
 - Support new --sol-payload-instance and --deactivate-all-instances
   options in ipmiconsole.
 - Fix ipmiseld compile issue with -Werror=format-security.

* Mon Aug 27 2012 Jan Safranek <jsafrane@redhat.com> - 1.2.1-1
- Reworked RPM scriptlets to use systemd-rpm macros (#850117).
- Updated to freeipmi-1.2.1:
 - Support new ipmiseld daemon, a daemon that regularly polls the SEL
   and stores the events to the local syslog.
 - In ipmipower, support --oem-power-type option to support OEM
   specific power control operations.  Included in this support were
   the follow changes to ipmipower:
   - Support initial OEM power type of C410X.
   - Re-architect to allow input of extra information for an OEM power
     operation via the '+' operator after the hostname.
   - Re-architect to allow input of target hostname multiple times
     under OEM power cases.
   - Re-architect to allow serialization of power control operations to
     the same host.
 - Globally in tools, support --target-channel-number and
   --target-slave-address to specify specific targets.
 - Globally in tools, support ability to specify alternate port via
   optional [:port] in hostname or host config.
 - In ipmi-fru, support --bridge-fru option to allow reading FRU entries
   from satellite controllers.
 - In bmc-config, add configuration support for
   Maximum_Privilege_Cipher_Suite_Id_15 under RMCPplus_Conf_Privilege.
 - Globally support Cipher Suite ID 15 and 16 based on comments from
   Intel.
 - In ipmi-sensors, support --output-sensor-thresholds, to allow
   outputting of sensor thresholds in default output for scripting.
 - In ipmi-sel, support new --post-clear option.
 - In bmc-device, support new --set-sensor-reading-and-event-status
   option.
 - In ipmi-oem, support additional Intel Node Manager commands,
   including:
   - get-node-manager-capabilities
   - node-manager-policy-control 
   - get-node-manager-policy
   - set-node-manager-policy
   - remove-node-manager-policy
   - get-node-manager-alert-thresholds
   - set-node-manager-alert-thresholds
   - get-node-manager-policy-suspend-periods
   - set-node-manager-policy-suspend-periods
   - set-node-manager-power-draw-range
 - In ipmi-oem, support Wistron OEM commands extensions.
 - In ipmi-sel, support Wistron OEM SEL interpretations.
 - In ipmi-fru, support Wistron OEM FRU records.
 - In ipmi-pef-config, support configuration volatile Alert String 0
   and Lan Alert Destination 0.

* Tue Jul 31 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.7-1
- Updated to freeipmi-1.1.7:
  - In ipmi-sensors and ipmi-sel, fix units output corner case.
  - In bmc-info, detect unsupported system info corner case.
  - Update documentation with motherboard support.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 17 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.6-3
- fixed License to GPLv3+

* Tue Jul 17 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.6-2
- fixed upstream URL

* Fri Jun 29 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.6-1
- Updated to freeipmi-1.1.6:
  - In ipmi-sel, support Supermicro SEL OEM interpretations in
    --output-event-state.
  - In ipmi-sel and ipmi-sensors, support additional sensor/SEL
    interpretations including:
    - System Firmware Progress Transition Severity
    - Button/Switch Transition Severity
    - Chassis Transition Severity
    - POST Memory Resize State
    - Cable/Interconnect Transition Severity
    - Boot Error Transition Severity
    - Slot Connector Transition Severity
    - Memory State
    - Memory Transition Severity
  - In bmc-config, ipmi-chassis-config, ipmi-pef-config, and
    ipmi-chassis-config, support cipher suite ID argument.
  - Support Supermicro X9DRi-F OEM sensors and events.
  - Fix Intel S2600JF/Appro 512x OEM SEL interpretations based on
    comments from Intel.
  - Support Supermicro SEL OEM interpretations.
  - Support new sensor/SEL interpretations.
  - Various documentation updates and fixes.

* Fri May 18 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.5-1
- Updated to freeipmi-1.1.5:
  - Support Supermicro OEM sensors/SEL on H8DGU-F motherboards.
  - In ipmiconsole, fix password length check bug.
  - In bmc-watchdog, fix --start-if-stopped and --reset-if-running
    options.
  - In ipmidetectd, fix usage output typos.
  - In ipmi-sensors-config, fix several parallel output corner cases.
  - For consistency to other tools, turn on quiet-caching if
    communicating with multiple hosts in bmc-device and ipmi-oem.
  - In ipmi-sensors, fix bug in which multiple workarounds could not be
    used or used in combination with bridging.
  - Fix start run levels in ipmidetectd init script. 
  - In libfreeipmi fru-parse API, handle additional device busy errors.
  - Various documentation updates.

* Fri Apr 20 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.4-1
- Updated to freeipmi-1.1.4:
  - In ipmi-oem, fix error message output in several Supermicro OEM
    commands.
  - In ipmi-oem, add Intel --get-power-restore-delay and
    --set-power-restore-delay support.
  - In ipmi-sel, support Intel S2600JF/Appro 512x OEM SEL
    interpretations.
  - In libfreeipmi, support new sensor and SEL event interpretations,
    including Session Audit, Voltage Limits.
  - In libfreeipmi, support new OEM interpretations for Intel S5000PAL
    NMI State and SMI timeout sensors/SEL events.
  - In libfreeipmi, support Intel S2600JF/Appro 512x OEM SEL
    interpretations.
  - Various documentation updates.

* Wed Mar  7 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.3-1
- Updated to freeipmi-1.1.3:
  - Support Supermicro CPU temperature SEL events.
  - In ipmi-oem, fix corner case with Dell C410x power control
    calculation.
  - In all tools, fix error messages to differentiate between invalid
    and unsupported cipher suite IDs.
  - In bmc-config, fix a Cipher Suite Privilege configuration
    corner case in the workaround for an HP DL145 workaround.
  - In bmc-config, add workaround for Cipher Suite Privilege
    configuration on Intel S2600JF/Appro 512X.
  - Various documentation updates.
  - In libfreeipmi, fix incorrect packet layout for the Get Lan
    Configuration Parameters RMCPplus Messaging Cipher Suite Entry Support
    response.
  - In libipmimonitoring, properly return connection timeout error on
    connection timeout.
  - Fix build when using --docdir. 
  - Various documentation updates.

* Wed Feb  8 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.2-1
- Updated to freeipmi-1.1.2:
  - In ipmi-oem, support new Dell C410x OEM extensions
    slot-power-toggle, slot-power-control, get-port-map, set-port-map.
  - Fix daemon setup race condition in ipmidetectd and bmc-watchdog that
    can affect systemd.
  - In ipmiconsole, support new --serial-keepalive-empty option.
  - In bmc-device, support new --rearm-sensor option.
  - In ipmi-oem, add additional Dell get-system-info options
  - slot-number
  - system-revision
  - embedded-video-status
  - idrac-info
  - idrac-ipv4-url
  - idrac-gui-webserver-control
  - cmc-ipv4-url,
  - cmc-ipv6-info
  - cmc-ipv6-url
  - In ipmi-oem, support Dell 12G mac addresses under get-system-info.   
  - In ipmi-sensors, some sensors that reported "Unknown" may now report
    "N/A" due to an interpretation change of several IPMI error codes.
  - In ipmi-sensors, workaround sensor reading issue on Sun Blade x6250
    and Sun Blade 6000M2.
  - Fix several freeipmi.conf config file parsing bugs.
  - In libipmiconsole, fix serial keepalive timeout calculation bug that
    can lead to excessive packets retransmitted.
  - In libipmiconsole, support new SERIAL_KEEPALIVE_EMPTY engine flag.
  - In libipmiconsole, do not deactivate a SOL payload if it appears the
    SOL payload has been stolen, but we did not receive a SOL deactivating
    flag.
  - In libipmiconsole, fix corner case in which session not closed
    cleanly when DEACTIVATE_ONLY flag specified.
  - In libipmiconsole, workaround bug in Dell Poweredge M605, M610, and
    M915 where instance count of SOL is always returned as 0.
  - In libfreeipmi, add functions for re-arm sensor events IPMI payload. 
  - In libfreeipmi/sensor-read, under some error conditions return error
    of "unavailable" instead of "cannot be obtained" error code.
  - In libfreeipmi/sensor-read, add workarounds to handle issues on Sun
    Blade x6250 and Sun Blade 6000M2.
  - Various documentation updates.
  - Redo formattig of include/freeipmi/templates/ documents.

* Fri Jan  6 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.1-2
- added systemd unit files (#767611)

* Wed Jan  4 2012 Jan Safranek <jsafrane@redhat.com> - 1.1.1-1
- Updated to freeipmi-1.1.1:
  - Support new tool ipmi-pet, tool to parse/interpret platform event
    traps.
  - Support new --sdr-cache-file option specify specific SDR cache file
    in all SDR related tools (ipmi-sensors, ipmi-sel, ipmi-fru, etc.).
  - In ipmi-fru, do not consider a busy device a fatal error. 
  - In ipmi-sensors, support 'ignoreauthcode' workaround option.
  - In ipmi-sensors, support Quanta QSSC-S4R/Appro GB812X-CN OEM SDRs
    and sensors.
  - In ipmi-sel, support Quanta QSSC-S4R/Appro GB812X-CN OEM SEL events.
  - In ipmi-sel, fix several OEM specific event output bugs.
  - In ipmi-pef-config, fix configuration bug for
    Enable_PEF_Event_Messages.
  - In ipmi-raw, for file/stdin input, output line number when there is
    an error.
  - Update libfreeipmi for DCMI 1.5 additions.
  - Update libfreeipmi fru-parse sub-library to support FRU parsing
    without an IPMI connection.
  - In libfreeipmi, support IPMI_FLAGS_NOSESSION flag to open a context
    for IPMI communication w/o establishing a session.
  - In libfreeipmi, support IPMI_FLAGS_NO_LEGAL_CHECK flag, to
    workaround motherboards to may return illegal IPMI packets.
  - In libfreeipmi, support IPMI_FLAGS_IGNORE_AUTHENTICATION_CODE flag,
    to workaround specific situations where motherboards return
    incorrectly generated authentication codes.
  - In libfreeipmi fru-parse sub-library, support
    IPMI_FRU_PARSE_ERR_DEVICE_BUSY error code.
  - In libfreeipmi, add support for IPMI firmware firewall and command
    discovery payloads.
  - In libfreeipmi, support Quanta QSSC-S4R/Appro GB812X-CN OEM SEL
    events.
  - Fix various macro names (typos, invalid naming, etc.)

* Wed Dec 14 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.10-1
- Updated to freeipmi-1.0.10:
  - Clarify bmc-watchdog error messages.
  - Various documentation updates.

* Tue Nov 22 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.9-1
- Updated to freeipmi-1.0.9:
  - Support Supermicro OEM sensors on X9SCA-F-O motherboards.
  - Support Supermicro OEM sensors on X9SCM-F motherboards with
    newer firmware.

* Thu Oct 27 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.8-1
- enable build on all archs, the iopl issue #368541 is fixed
- Updated to freeipmi-1.0.8:
  - Fix corner case in which invalid SDR entry could be loaded when
    shared sensors exist on event only records.
  - Fix several event output corner cases.
  - Fix 'assumesystemevent' workaround for ipmi-sel.
  - Fix ipmi-raw and ipmi-oem allocation bug on newer systems, such as
    RHEL6.
  - Support Intel Node Manager sensor/SEL events for Intel S2600JF/Appro
      512X.
  - Document workarounds for Intel S2600JF/Appro 512X.
  - Per definition, output GUID w/ lower case characters in bmc-info.
  - Other minor bug fixes.

* Thu Sep 29 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.7-1
- Updated to freeipmi-1.0.7:
  - Support many new sensor state and sel event interpretations.
  - Fix parsing bugs for freeipmi_interpret_sel.conf.
  - Support 'assumebmcowner' workaround in ipmi-sensors.
  - Support dynamic linking in libfreeipmi.
  - Output pidfile in bmc-watchdog to support easier init script killing.
  - Do not poll stdin in ipmipower when operating in non-interactive mode.
  - Support IGNORE_SCANNING_DISABLED workaround in libipmimonitoring.
  - Support Supermicro OEM sensors on X7DB8, X8DTN, X7SBI-LN4, X8DTL,
    X8DTN+-F, and X8SIE motherboards.
  - Fix handling error codes in optional parts of ipmi-dcmi.
  - Fix various debug dumping bugs.
  - Fix ipmimonitoring script install bug on some systems.
  - Fix symbol global vs. locals in libipmimonitoring.
  - Minor documentation and manpage updates.

* Mon Sep  5 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.6-1
- Updated to freeipmi-1.0.6:
  - Support 'ignorescanningdisabled' workaround in ipmi-sensors.
  - Support Supermicro X8SIL-F, X9SCL, and X9SCM motherboard OEM sensors.
  - Update bmc-watchdog logrotate script to reduce unnecessary output.
  - Fix ipmi-fru output typo.

* Fri Jul  1 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.5-1
- Updated to freeipmi-1.0.5:
  - Fix various issues in ipmi-dcmi, including command line parsing
    bugs, asset tag/string identifier overwriting, and fix assumptions
    based on new information in v1.5 errata.
  - Support pkg-config files for libraries.
  - Various documentation updates.

* Fri Apr 22 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.4-1
- Updated to freeipmi-1.0.4:
  - Support "discretereading" workaround in ipmi-sensors and associated
    libraries.
  - Support "spinpoll" workaround/performance optimization in tools and
    libraries.
  - Support additional sensor/SEL interpretations for Intel motherboards.
  - Add convenience input checking functions to libipmiconsole.
  - Fix bug in libipmimonitoring to allow additional OEM interpretations.

* Wed Mar 30 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.3-1
- Updated to freeipmi-1.0.3, see announce at
  http://lists.gnu.org/archive/html/freeipmi-users/2011-03/msg00017.html

* Wed Feb 23 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.2-1
- Updated to freeipmi-1.0.2, see announce at
  http://lists.gnu.org/archive/html/freeipmi-users/2011-02/msg00027.html

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 21 2011 Jan Safranek <jsafrane@redhat.com> - 1.0.1:1
- Updated to freeipmi-1.0.1, see announce at
  http://lists.gnu.org/archive/html/freeipmi-users/2011-01/msg00006.html
- Configuration files moved from /etc/ to /etc/freeipmi/. Support legacy config
  files for backwards compatibility.
- More detailed release information can be found in the NEWS file.

