%global peclName  xmldiff

%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}

%if 0%{?fedora} < 21
# After dom
%global ini_name %peclName.ini
%else
# After 20-dom
%global ini_name 40-%peclName.ini
%endif

Name:             php-pecl-%peclName
Version:          0.9.2
Release:          4%{?dist}
Summary:          Pecl package for XML diff and merge
Group:            Development/Languages

License:          BSD
URL:              http://pecl.php.net/package/%peclName
Source0:          http://pecl.php.net/get/%peclName-%{version}.tgz

BuildRequires:    php-pear
BuildRequires:    php-devel
BuildRequires:    libxml2-devel, diffmark-devel, dos2unix
# dom.so needed by %%check
Requires:         php-dom%{_isa}, php-libxml%{?_isa}
BuildRequires:    php-dom%{_isa}, php-libxml%{?_isa}
Requires(post):   %{__pecl}
Requires(postun): %{__pecl}
Requires:         php(zend-abi) = %{php_zend_api}
Requires:         php(api) = %{php_core_api}
Requires:         php-xml

Provides:         php-%peclName = %{version}
Provides:         php-%peclName%{?_isa} = %{version}

# Filter private shared (RPM 4.9) (f20+ (and rhel7) does not require that)
%if 0%{?fedora} < 20 && 0%{?rhel} < 7
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$
%endif

%description
The extension is able to produce diffs of two XML documents and then
to apply the difference to the source document. The diff
is a XML document containing copy/insert/delete instruction nodes in
human readable format. DOMDocument objects, local files and strings in
memory can be processed.


%prep
%setup -qc

#rm bundled diffmark
rm -rf %peclName-%{version}/diffmark

# to make rpmlint happy
dos2unix --keepdate %peclName-%{version}/LICENSE

%build
cd %peclName-%{version}
phpize
%{configure} --with-%peclName --with-libdiffmark=%{_libdir}
make %{?_smp_mflags}


%install
cd %peclName-%{version}

make %{?_smp_mflags} install INSTALL_ROOT=%{buildroot}

# Install XML package description
install -m 0755 -d %{buildroot}%{pecl_xmldir}
install -m 0664 ../package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml
install -d %{buildroot}%{php_inidir}
# install config file
install -d %{buildroot}%{php_inidir}
cat << 'EOF' | tee %{buildroot}%{php_inidir}/%{ini_name}
extension=%{php_extdir}/%peclName.so
EOF

mkdir -p %{buildroot}/%{pecl_docdir}/%peclName/
mv {CREDITS,LICENSE} %{buildroot}/%{pecl_docdir}/%peclName/

rm -rf %{buildroot}/%{_includedir}/php/ext/%peclName/

%check
# only check if build extension can be loaded
php \
    --no-php-ini \
    --define extension=dom.so \
    --define extension=%{buildroot}%{php_extdir}/%peclName.so \
    --modules | grep %peclName

cd %peclName-%{version}

# Can't do just 'make %{?_smp_mflags} test' because path and option hardcoded. Makefile patching needed or run tests manually
TEST_PHP_EXECUTABLE=%{__php} \
  NO_INTERACTION=1 \
    TEST_PHP_ARGS="-n -d extension=dom.so -d extension=%{buildroot}%{php_extdir}/%peclName.so" \
      php -n run-tests.php

%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ "$1" -eq "0" ]; then
  %{pecl_uninstall} %peclName >/dev/null || :
fi

%files
%doc %{pecl_docdir}/%peclName
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%peclName.so
%{pecl_xmldir}/%{name}.xml

%changelog
* Wed May 14 2014 Pavel Alexeev <Pahan@Hubbitus.info> - 0.9.2-4
- Own %%{pecl_docdir}/%%peclName dir.

* Tue May 13 2014 Pavel Alexeev <Pahan@Hubbitus.info> - 0.9.2-3
- Surround filter provides by condition %%if 0%%{?fedora} < 20 && 0%%{?rhel} < 7
- Fix %%doc installation issue.

* Mon May 12 2014 Pavel Alexeev <Pahan@Hubbitus.info> - 0.9.2-2
- Changes by Fedora review bz#1094864 from Remi Collet comments.
- Remove define php_apiver, php_extdir.
- Tun upstream tests in %%check.
- Requires php-dom%%{_isa} and php-libxml%%{?_isa} instead of php-xml.
- Install docs into %%pecl_docdir.
- Prefix ini file with numeric value in rawhide.
- Drop protect %%{pecl_uninstall} present.

* Tue May 6 2014 Pavel Alexeev <Pahan@Hubbitus.info> - 0.9.2-1
- Initial spec
