# for -O3 on ppc64 c.f. 1051068
%global _performance_build 1

Summary: Library providing XML and HTML support
Name: libxml2
Version: 2.9.2
Release: 1%{?dist}
License: MIT
Group: Development/Libraries
Source: ftp://xmlsoft.org/libxml2/libxml2-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python python-devel zlib-devel pkgconfig xz-devel
URL: http://xmlsoft.org/
Patch0: libxml2-multilib.patch
Patch1: libxml2-2.9.0-do-not-check-crc.patch

#Patch100: libxml2-Fix-a-regression-in-xmlGetDocCompressMode.patch
#Patch101: CVE-2014-3660-rhel7.patch

%description
This library allows to manipulate XML files. It includes support
to read, modify and write XML and HTML files. There is DTDs support
this includes parsing and validation even with complex DtDs, either
at parse time or later once the document has been modified. The output
can be a simple SAX stream or and in-memory DOM like representations.
In this case one can use the built-in XPath and XPointer implementation
to select sub nodes or ranges. A flexible Input/Output mechanism is
available, with existing HTTP and FTP modules and combined to an
URI library.

%package devel
Summary: Libraries, includes, etc. to develop XML and HTML applications
Group: Development/Libraries
Requires: libxml2 = %{version}-%{release}
Requires: zlib-devel
Requires: xz-devel
Requires: pkgconfig

%description devel
Libraries, include files, etc you can use to develop XML applications.
This library allows to manipulate XML files. It includes support
to read, modify and write XML and HTML files. There is DTDs support
this includes parsing and validation even with complex DtDs, either
at parse time or later once the document has been modified. The output
can be a simple SAX stream or and in-memory DOM like representations.
In this case one can use the built-in XPath and XPointer implementation
to select sub nodes or ranges. A flexible Input/Output mechanism is
available, with existing HTTP and FTP modules and combined to an
URI library.

%package static
Summary: Static library for libxml2
Group: Development/Libraries
Requires: libxml2 = %{version}-%{release}

%description static
Static library for libxml2 provided for specific uses or shaving a few
microseconds when parsing, do not link to them for generic purpose packages.

%package python
Summary: Python bindings for the libxml2 library
Group: Development/Libraries
Requires: libxml2 = %{version}-%{release}

%description python
The libxml2-python package contains a module that permits applications
written in the Python programming language to use the interface
supplied by the libxml2 library to manipulate XML files.

This library allows to manipulate XML files. It includes support
to read, modify and write XML and HTML files. There is DTDs support
this includes parsing and validation even with complex DTDs, either
at parse time or later once the document has been modified.

%prep
%setup -q
%patch0 -p1
# workaround for #877567 - Very weird bug gzip decompression bug in "recent" libxml2 versions
%patch1 -p1 -b .do-not-check-crc

#%%patch100 -p1
#%%patch101 -p1

%build
%configure
make %{_smp_mflags}

%install
rm -fr %{buildroot}

make install DESTDIR=%{buildroot}

# multiarch crazyness on timestamp differences or Makefile/binaries for examples
touch -m --reference=$RPM_BUILD_ROOT/%{_includedir}/libxml2/libxml/parser.h $RPM_BUILD_ROOT/%{_bindir}/xml2-config

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/python*/site-packages/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/python*/site-packages/*.la
rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/libxml2-%{version}/*
rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/libxml2-python-%{version}/*
(cd doc/examples ; make clean ; rm -rf .deps Makefile)
gzip -9 -c doc/libxml2-api.xml > doc/libxml2-api.xml.gz

%check
make runtests

%clean
rm -fr %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root)

%doc AUTHORS NEWS README Copyright TODO
%doc %{_mandir}/man1/xmllint.1*
%doc %{_mandir}/man1/xmlcatalog.1*
%doc %{_mandir}/man3/libxml.3*

%{_libdir}/lib*.so.*
%{_bindir}/xmllint
%{_bindir}/xmlcatalog

%files devel
%defattr(-, root, root)

%doc %{_mandir}/man1/xml2-config.1*
%doc AUTHORS NEWS README Copyright
%doc doc/*.html doc/html doc/*.gif doc/*.png
%doc doc/tutorial doc/libxml2-api.xml.gz
%doc doc/examples
%doc %dir %{_datadir}/gtk-doc/html/libxml2
%doc %{_datadir}/gtk-doc/html/libxml2/*.devhelp
%doc %{_datadir}/gtk-doc/html/libxml2/*.html
%doc %{_datadir}/gtk-doc/html/libxml2/*.png
%doc %{_datadir}/gtk-doc/html/libxml2/*.css

%{_libdir}/lib*.so
%{_libdir}/*.sh
%{_includedir}/*
%{_bindir}/xml2-config
%{_datadir}/aclocal/libxml.m4
%{_libdir}/pkgconfig/libxml-2.0.pc
%{_libdir}/cmake/%{name}/libxml2-config.cmake

%files static
%defattr(-, root, root)

%{_libdir}/*a

%files python
%defattr(-, root, root)

%{_libdir}/python*/site-packages/libxml2.py*
%{_libdir}/python*/site-packages/drv_libxml2.py*
%{_libdir}/python*/site-packages/libxml2mod*
%doc python/TODO
%doc python/libxml2class.txt
%doc python/tests/*.py
%doc doc/*.py
%doc doc/python.html

%changelog
* Fri Nov 21 2014 Alice Wonder <rpmbuild@domblogger.net> - 2.9.2-1
- Update to 2.9.2

* Sat Oct 11 2014 Daniel Veillard <veillard@redhat.com> - 2.9.1-5.1
- CVE-2014-3660 denial of service via recursive entity expansion (rhbz#1149087)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 2.9.1-5
- Mass rebuild 2014-01-24

* Wed Jan 15 2014 Daniel Veillard <veillard@redhat.com> - 2.9.1-4
- rebuild to activate -O3 on ppc64 rhbz#1051068

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.9.1-3
- Mass rebuild 2013-12-27

* Fri Nov 15 2013 Daniel Veillard <veillard@redhat.com> - 2.9.1-2
- Fix a regression in xmlGetDocCompressMode() rhbz#963716

* Fri Apr 19 2013 Daniel Veillard <veillard@redhat.com> - 2.9.1-1
- upstream release of 2.9.1
- a couple more API entry point
- compatibility with python3
- a lot of bug fixes

* Mon Feb 11 2013 Daniel Veillard <veillard@redhat.com> - 2.9.0-4
- fix --nocheck build which I broke in october rhbz#909767

* Mon Nov 19 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.9.0-3
- workaround for crc/len check failure, rhbz#877567

* Thu Oct 11 2012 Daniel Veillard <veillard@redhat.com> - 2.9.0-2
- remaining cleanups from merge bug rhbz#226079
- do not put the docs in the main package, only in -devel rhbz#864731

* Tue Sep 11 2012 Daniel Veillard <veillard@redhat.com> - 2.9.0-1
- upstream release of 2.9.0
- A few new API entry points
- More resilient push parser mode
- A lot of portability improvement
- Faster XPath evaluation
- a lot of bug fixes and smaller improvement

* Fri Aug 10 2012 Daniel Veillard <veillard@redhat.com> - 2.9.0-0rc1
- upstream release candidate 1 of 2.9.0
- introduce a small API change, but ABI compatible, see
  https://mail.gnome.org/archives/xml/2012-August/msg00005.html
  patches for php, gcc/libjava and evolution-data-connector are upstream
  Grab me in cases of problems veillard@redhat.com
- many bug fixes including security aspects and small improvements

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 23 2012 Daniel Veillard <veillard@redhat.com> - 2.8.0-1
- upstream release of 2.8.0
- add lzma compression support
- many bug fixes and small improvements

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.8-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Mar  4 2011 Daniel Veillard <veillard@redhat.com> - 2.7.8-6
- fix a double free in XPath CVE-2010-4494 bug 665965

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Nov  5 2010 Daniel Veillard <veillard@redhat.com> - 2.7.8-4
- reactivate shared libs versionning script

* Thu Nov  4 2010 Daniel Veillard <veillard@redhat.com> - 2.7.8-1
- Upstream release of 2.7.8
- various bug fixes, including potential crashes
- new non-destructive formatting option
- date parsing updated to RFC 5646

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 2.7.7-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Mon Mar 15 2010 Daniel Veillard <veillard@redhat.com> - 2.7.7-1
- Upstream release of 2.7.7
- fix serious trouble with zlib >= 1.2.4
- xmllint new option --xpath
- various HTML parser improvements
- includes a number of nug fixes

* Tue Oct  6 2009 Daniel Veillard <veillard@redhat.com> - 2.7.6-1
- Upstream release of 2.7.6
- restore thread support off by default in 2.7.5

* Thu Sep 24 2009 Daniel Veillard <veillard@redhat.com> - 2.7.5-1
- Upstream release of 2.7.5
- fix a couple of Relax-NG validation problems
- couple more fixes

* Tue Sep 15 2009 Daniel Veillard <veillard@redhat.com> - 2.7.4-2
- fix a problem with little data at startup affecting inkscape #523002

* Thu Sep 10 2009 Daniel Veillard <veillard@redhat.com> - 2.7.4-1
- upstream release 2.7.4
- symbol versioning of libxml2 shared libs
- very large number of bug fixes

* Mon Aug 10 2009 Daniel Veillard <veillard@redhat.com> - 2.7.3-4
- two patches for parsing problems CVE-2009-2414 and CVE-2009-2416

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 18 2009 Daniel Veillard <veillard@redhat.com> - 2.7.3-1
- new release 2.7.3
- limit default max size of text nodes
- special parser mode for PHP
- bug fixes and more compiler checks

* Wed Dec  3 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.7.2-7
- Pull back into Python 2.6

* Wed Dec  3 2008 Caolán McNamara <caolanm@redhat.com> - 2.7.2-6
- AutoProvides requires BuildRequires pkgconfig

* Wed Dec  3 2008 Caolán McNamara <caolanm@redhat.com> - 2.7.2-5
- rebuild to get provides(libxml-2.0) into HEAD rawhide

* Mon Dec  1 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.7.2-4
- Rebuild for pkgconfig logic

* Fri Nov 28 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.7.2-3
- Rebuild for Python 2.6

* Wed Nov 12 2008 Daniel Veillard <veillard@redhat.com> - 2.7.2-2.fc11
- two patches for size overflows problems CVE-2008-4225 and CVE-2008-4226

* Fri Oct  3 2008 Daniel Veillard <veillard@redhat.com> 2.7.2-1.fc10
- new release 2.7.2
- Fixes the known problems in 2.7.1
- increase the set of options when saving documents

* Thu Oct  2 2008 Daniel Veillard <veillard@redhat.com> 2.7.1-2.fc10
- fix a nasty bug in 2.7.x, http://bugzilla.gnome.org/show_bug.cgi?id=554660

* Mon Sep  1 2008 Daniel Veillard <veillard@redhat.com> 2.7.1-1.fc10
- fix python serialization which was broken in 2.7.0
- Resolve: rhbz#460774

* Sat Aug 30 2008 Daniel Veillard <veillard@redhat.com> 2.7.0-1.fc10
- upstream release of 2.7.0
- switch to XML 1.0 5th edition
- switch to RFC 3986 for URI parsing
- better entity handling
- option to remove hardcoded limitations in the parser
- more testing
- a new API to allocate entity nodes
- and lot of fixes and clanups

* Mon Aug 25 2008 Daniel Veillard <veillard@redhat.com> 2.6.32-4.fc10
- fix for entities recursion problem
- Resolve: rhbz#459714

* Fri May 30 2008 Daniel Veillard <veillard@redhat.com> 2.6.32-3.fc10
- cleanup based on Fedora packaging guidelines, should fix #226079
- separate a -static package

* Thu May 15 2008 Daniel Veillard <veillard@redhat.com> 2.6.32-2.fc10
- try to fix multiarch problems like #440206

* Tue Apr  8 2008 Daniel Veillard <veillard@redhat.com> 2.6.32-1.fc9
- upstream release 2.6.32 see http://xmlsoft.org/news.html
- many bug fixed upstream

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.6.31-2
- Autorebuild for GCC 4.3

* Fri Jan 11 2008 Daniel Veillard <veillard@redhat.com> 2.6.31-1.fc9
- upstream release 2.6.31 see http://xmlsoft.org/news.html
- many bug fixed upstream

* Thu Aug 23 2007 Daniel Veillard <veillard@redhat.com> 2.6.30-1
- upstream release 2.6.30 see http://xmlsoft.org/news.html
- many bug fixed upstream

* Tue Jun 12 2007 Daniel Veillard <veillard@redhat.com> 2.6.29-1
- upstream release 2.6.29 see http://xmlsoft.org/news.html
- many bug fixed upstream

* Wed May 16 2007 Matthias Clasen <mclasen@redhat.com> 2.6.28-2
- Bump revision to fix N-V-R problem

* Tue Apr 17 2007 Daniel Veillard <veillard@redhat.com> 2.6.28-1
- upstream release 2.6.28 see http://xmlsoft.org/news.html
- many bug fixed upstream

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 2.6.27-2
- rebuild against python 2.5

* Wed Oct 25 2006 Daniel Veillard <veillard@redhat.com> 2.6.27-1
- upstream release 2.6.27 see http://xmlsoft.org/news.html
- very large amount of bug fixes reported upstream

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.6.26-2.1.1
- rebuild

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.6.26-2.1
- rebuild

* Wed Jun  7 2006 Daniel Veillard <veillard@redhat.com> 2.6.26-2
- fix bug #192873
* Tue Jun  6 2006 Daniel Veillard <veillard@redhat.com> 2.6.26-1
- upstream release 2.6.26 see http://xmlsoft.org/news.html

* Tue Jun  6 2006 Daniel Veillard <veillard@redhat.com>
- upstream release 2.6.25 broken, do not ship !

