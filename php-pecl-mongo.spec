%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}

%global pecl_name   mongo
%global with_zts    0%{?__ztsphp:1}
%global gh_commit   a3335ff08327b2c429ad5a2b712ed54b42e90d36
%global gh_short    %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner    mongodb
%global gh_project  mongo-php-driver
%global with_tests  %{?_with_tests:1}%{!?_with_tests:0}
%if "%{php_version}" < "5.6"
# After json
%global ini_name    %{pecl_name}.ini
%else
# After 40-json
%global ini_name    50-%{pecl_name}.ini
%endif

Summary:      PHP MongoDB database driver
Name:         php-pecl-mongo
Version:      1.5.8
Release:      1%{?dist}
License:      ASL 2.0
Group:        Development/Languages
URL:          http://pecl.php.net/package/%{pecl_name}

# Pull sources from github to get tests
Source0:      https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{version}%{?prever}.tar.gz
Source1:      %{pecl_name}.ini

BuildRequires: php-devel >= 5.2.6
BuildRequires: php-pear
BuildRequires: cyrus-sasl-devel
%if %{with_tests}
BuildRequires: php-json
BuildRequires: mongodb
BuildRequires: mongodb-server
%endif

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}

Provides:     php-%{pecl_name} = %{version}
Provides:     php-%{pecl_name}%{?_isa} = %{version}
Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared provides
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This package provides an interface for communicating with the
MongoDB database in PHP.

Documentation: http://php.net/mongo


%prep
%setup -c -q

mv %{gh_project}-%{gh_commit} NTS
cp %{SOURCE1} %{ini_name}
mv NTS/package.xml .

cd NTS
# Sanity check, really often broken
extver=$(sed -n '/#define PHP_MONGO_VERSION/{s/.* "//;s/".*$//;p}' php_mongo.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

%if %{with_zts}
cp -pr NTS ZTS
%endif


%build
cd NTS
%{_bindir}/phpize
%configure  \
  --with-mongo-sasl \
  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure  \
  --with-mongo-sasl \
  --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}

make -C NTS install INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ "$1" -eq "0" ]; then
   %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%check
: Minimal load test for NTS extension
%{__php} -n \
    -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    -i | grep "MongoDB Support => enabled"

%if %{with_tests}
cd NTS

: Create the configuration file
mkdir data
sed -e "/DBDIR/s:/data:$PWD/data:" \
    tests/utils/cfg.inc.template   \
    >tests/utils/cfg.inc

: Launch the test servers
MONGO_SERVER_STANDALONE=yes \
MONGO_SERVER_STANDALONE_AUTH=yes \
MONGO_SERVER_REPLICASET=yes \
MONGO_SERVER_REPLICASET_AUTH=yes \
make servers

: Ignore 2 tests
# need investigation (pass in local build)
rm tests/generic/bug00667.phpt
# fails with "hmh. you have to fast server!"
rm tests/standalone/bug01036-001.phpt

: Upstream test suite NTS extension
ret=0
TEST_PHP_EXECUTABLE=/usr/bin/php \
TEST_PHP_ARGS="-n -d extension=json.so -d extension=$PWD/modules/mongo.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php --show-diff || ret=1

: Cleanups
make stop-servers
rm -rf data

[ $ret -eq 0 ] || exit $ret
%endif

%if %{with_zts}
: Minimal load test for ZTS extension
%{__ztsphp} -n \
    -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    -i | grep "MongoDB Support => enabled"
%endif


%files
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Wed Nov 12 2014 Remi Collet <remi@fedoraproject.org> - 1.5.8-1
- Update to 1.5.8 (stable)

* Tue Sep 16 2014 Remi Collet <remi@fedoraproject.org> - 1.5.7-1
- Update to 1.5.7 (stable)

* Wed Jul 30 2014 Remi Collet <remi@fedoraproject.org> - 1.5.5-1
- Update to 1.5.5 (stable)

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.5.4-2
- rebuild for https://fedoraproject.org/wiki/Changes/Php56

* Tue Jun 17 2014 Remi Collet <remi@fedoraproject.org> - 1.5.4-1
- Update to 1.5.4 (stable)

* Fri Jun 06 2014 Remi Collet <remi@fedoraproject.org> - 1.5.3-1
- Update to 1.5.3 (stable)
- drop dependency on php-json

* Thu Apr 24 2014 Remi Collet <rcollet@redhat.com> - 1.5.1-2
- add numerical prefix to extension configuration file

* Sat Apr 05 2014 Remi Collet <remi@fedoraproject.org> - 1.5.1-1
- Update to 1.5.1 (stable)
- mongo.native_long not allowed on 32bits

* Fri Apr  4 2014 Remi Collet <remi@fedoraproject.org> - 1.5.0-1
- Update to 1.5.0 (stable)
- use sources from github for tests
- run upstream test suite when build --with tests
- mongo.ini cleanup
- enable SASL support
- install doc in pecl doc_dir
- build ZTS extension
- spec cleanup
- provides php-mongo

* Sat Nov  2 2013 Christof Damian <christof@damian.net> - 1.4.4-1
- upstream 1.4.4

* Thu Jul 25 2013 Christof Damian <christof@damian.net> - 1.4.2-1
- upstream 1.4.2

* Sat May 25 2013 Christof Damian <christof@damian.net> - 1.4.0-1
- upstream 1.4.0

* Thu Apr 18 2013 Christof Damian <christof@damian.net> - 1.3.7-1
- upstream 1.3.7

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 1.3.5-1
- update to 1.3.5
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Sat Feb 23 2013 Christof Damian <christof@damian.net> - 1.3.4-1
- upstream 1.3.4

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jan 13 2013 Christof Damian <christof@damian.net> - 1.3.2-1
- upstream 1.3.2

* Sat Jul 28 2012 Christof Damian <christof@damian.net> - 1.2.12-1
- upstream 1.2.12

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  9 2012 Christof Damian <christof@damian.net> - 1.2.10-1
- upstream 1.2.10

* Sat Mar  3 2012 Christof Damian <christof@damian.net> - 1.2.9-1
- upstream 1.2.9

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.2.7-1
- update to 1.2.7 for php 5.4
- fix filters

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Jul 17 2011 Christof Damian <christof@damian.net> - 1.2.1-1
- upstream 1.2.1

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Oct 25 2010 Christof Damian <christof@damian.net> - 1.0.10-4
- added link to option docs

* Sat Oct 23 2010 Christof Damian <christof@damian.net> - 1.0.10-3
- fix post
- add example config with sensible defaults
- add conditionals for EPEL + fix for check

* Fri Oct 22 2010 Christof Damian <christof@damian.net> - 1.0.10-2
- fixes for package review: requires and warnings

* Wed Oct 20 2010 Christof Damian <christof@damian.net> - 1.0.10-1
- Initial RPM
