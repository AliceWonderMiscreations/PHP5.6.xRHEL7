%global	php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:		%{expand:	%%global __pecl	%{_bindir}/pecl}}
%{!?php_extdir:	%{expand:	%%global php_extdir	%(php-config --extension-dir)}}

%global peclName  imagick
%global prever    RC1

Summary:		Provides a wrapper to the ImageMagick library
Name:		php-pecl-%peclName
Version:		3.2.0
Release:		0.3.%{prever}%{?dist}
License:		PHP
Group:		Development/Libraries
Source0:		http://pecl.php.net/get/%peclName-%{version}%{?prever}.tgz
Source1:		%peclName.ini
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
URL:			http://pecl.php.net/package/%peclName
BuildRequires:	php-pear >= 1.4.7
BuildRequires: php-devel >= 5.1.3
#Make sure we get the newer ImageMagick-devel with webp support
BuildRequires: ImageMagick-devel >= 6.8.9.8
Requires(post):	%{__pecl}
Requires(postun):	%{__pecl}
%if 0%{?php_zend_api:1}
Requires:		php(zend-abi) = %{php_zend_api}
Requires:		php(api) = %{php_core_api}
%else
Requires:		php-api = %{php_apiver}
%endif
Provides:		php-pecl(%peclName) = %{version}

Conflicts:	php-pecl-gmagick

# http://svn.php.net/viewvc?view=revision&revision=329769
#Patch0:		imagick-3.1.0RC1-IM-so6.patch

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
%peclName is a native php extension to create and modify images using the
ImageMagick API.
This extension requires ImageMagick version 6.2.4+ and PHP 5.1.3+.

IMPORTANT: Version 2.x API is not compatible with earlier versions.

%prep
%setup -qc

#cd %peclName-%{version}%{?prever}
#%%patch0 -p3 -b .im-so6

%build
cd %peclName-%{version}%{?prever}
phpize
%{configure} --with-%peclName
%{__make}

%install
rm -rf %{buildroot}

cd %peclName-%{version}%{?prever}

%{__make} install \
	INSTALL_ROOT=%{buildroot}

# Install XML package description
install -m 0755 -d %{buildroot}%{pecl_xmldir}
install -m 0664 ../package.xml %{buildroot}%{pecl_xmldir}/%peclName.xml
install -d %{buildroot}%{_sysconfdir}/php.d/
install -m 0664 %{SOURCE1} %{buildroot}%{_sysconfdir}/php.d/%peclName.ini

rm -rf %{buildroot}/%{_includedir}/php/ext/%peclName/

%check
# simple module load test
pushd %peclName-%{version}%{?prever}
php --no-php-ini \
    --define extension_dir=%{buildroot}%{php_extdir} \
    --define extension=%peclName.so \
    --modules | grep %peclName

%clean
rm -rf %{buildroot}

%post
%if 0%{?pecl_install:1}
%{pecl_install} %{pecl_xmldir}/%peclName.xml
%endif

%postun
%if 0%{?pecl_uninstall:1}
if [ "$1" -eq "0" ]; then
	%{pecl_uninstall} %peclName
fi
%endif

%files
%defattr(-,root,root,-)
%doc %peclName-%{version}%{?prever}/examples %peclName-%{version}%{?prever}/CREDITS
%{php_extdir}/%peclName.so
%{pecl_xmldir}/%peclName.xml
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/php.d/%peclName.ini

%changelog
* Thu Dec 18 2014 Alice Wonder <rpmbuild@domblogger.net> - 3.2.0-0.3.RC1
- Build against newer ImageMagick version

* Wed Oct 22 2014 Alice Wonder <rpmbuild@domblogger.net> - 3.2.0-0.2.RC1
- Build against ImageMagick w/ WebP support

* Fri Sep 19 2014 Alice Wonder <rpmbuild@domblogger.net> - 3.2.0-0.1.RC1
- Build against php 5.6.0 for CentOS 7

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-0.7.RC2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 3.1.0-0.6.RC2
- update to 3.1.0RC2
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Sat Mar 16 2013 Pavel Alexeev <Pahan@Hubbitus.info> - 3.1.0-0.5.RC1
- Rebuild to ImageMagick soname change (ml: http://www.mail-archive.com/devel@lists.fedoraproject.org/msg57163.html).
	Thanks to Remi Collet for the patch: http://svn.php.net/viewvc?view=revision&revision=329769

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-0.4.RC1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-0.3.RC1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Mar 4 2012 Pavel Alexeev <Pahan@Hubbitus.info> - 3.1.0-0.2.RC1
- Rebuild to ImageMagick soname change.

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 3.1.0-0.1.RC1
- update to 3.1.0RC1 for php 5.4
- add filter to avoid private-shared-object-provides
- add minimal %%check

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Sep 12 2011 Pavel Alexeev <Pahan@Hubbitus.info> - 3.0.0-10
- Fix FBFS f16-17. Bz#716201

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 jkeating - 3.0.0-8
- Rebuilt for gcc bug 634757

* Thu Sep 16 2010 Pavel Alexeev <Pahan@Hubbitus.info> - 3.0.0-7
- Rebuild against new ImageMagick

* Fri Jul 23 2010 Pavel Alexeev <Pahan@Hubbitus.info> - 3.0.0-6
- Update to 3.0.0
- Add Conflicts: php-pecl-gmagick - BZ#559675
- Delete new and unneeded files "rm -rf %%{buildroot}/%%{_includedir}/php/ext/%%peclName/"

* Sat May 15 2010 Pavel Alexeev <Pahan@Hubbitus.info> - 2.3.0-5
- New version 2.3.0

* Wed Mar 24 2010 Mike McGrath <mmcgrath@redhat.com> - 2.2.2-4.1
- Rebuilt for broken dep fix

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Remi Collet <Fedora@FamilleCollet.com> - 2.2.2-3
- rebuild for new PHP 5.3.0 ABI (20090626)

* Tue Mar 10 2009 Pavel Alexeev <Pahan@Hubbitus.info> - 2.2.2-2
- Rebuild due ImageMagick update

* Sat Feb 28 2009 Pavel Alexeev <Pahan@Hubbitus.info> - 2.2.2-1
- Step to version 2.2.2

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 11 2009 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.1-3
- All modifications in this release inspired by Fedora review by Remi Collet.
- Add versions to BR for php-devel and ImageMagick-devel
- Remove -n option from %%setup which was excessive with -c
- Module install/uninstall actions surround with %%if 0%{?pecl_(un)?install:1} ... %%endif
- Add Provides: php-pecl(%peclName) = %{version}

* Sat Jan 3 2009 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.1-2
- License changed to PHP (thanks to Remi Collet)
- Add -c flag to %%setup (Remi Collet)
	And accordingly it "cd %%peclName-%%{version}" in %%build and %%install steps.
- Add (from php-pear template)
	Requires(post):	%%{__pecl}
	Requires(postun):	%%{__pecl}
- Borrow from Remi Collet php-api/abi requirements.
- Use macroses: (Remi Collet)
	%%pecl_install instead of direct "pear install --soft --nobuild --register-only"
	%%pecl_uninstall instead of pear "uninstall --nodeps --ignore-errors --register-only"
- %%doc examples/{polygon.php,captcha.php,thumbnail.php,watermark.php} replaced by %%doc examples (Remi Collet)
- Change few patchs to macroses: (Remi Collet)
	%%{_libdir}/php/modules - replaced by %%{php_extdir}
	%%{xmldir} - by %%{pecl_xmldir}
- Remove defines of xmldir, peardir.
- Add 3 recommended macroses from doc http://fedoraproject.org/wiki/Packaging/PHP : php_apiver, __pecl, php_extdir

* Sat Dec 20 2008 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.1-1
- Step to version 2.2.1
- As prepare to push it into Fedora:
	- Change release to 1%%{?dist}
	- Set setup quiet
	- Escape all %% in changelog section
	- Delete dot from summary
	- License change from real "PHP License" to BSD (by example with php-peck-phar and php-pecl-xdebug)
- %%defattr(-,root,root,-) changed to %%defattr(-,root,root,-)

* Mon May 12 2008 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] spb [ dOt.] su> - 2.2.0b2-0.Hu.0
- Step to version 2.2.0b2
- %%define	peclName	imagick and replece to it all direct appearances.

* Thu Mar 6 2008 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] info> - 2.1.1RC1-0.Hu.0
- Steep to version 2.1.1RC1 -0.Hu.0
- Add Hu-part and %%{?dist} into Release
- Add BuildRequires: ImageMagick-devel

* Fri Oct 12 2007 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] info> - 2.0.0RC1
- Global rename from php-pear-imagick to php-pecl-imagick. This is more correct.

* Wed Aug 22 2007 Pavel Alexeev <Pahan [ at ] Hubbitus [ DOT ] info> - 2.0.0RC1
- Initial release. (Re)Written from generated (pecl make-rpm-spec)
