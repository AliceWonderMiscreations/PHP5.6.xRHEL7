PHP5.6.xRHEL7
=============

RPM spec files for PHP 5.6.x for RHEL 7

Binary (and src) RPMs for x86_64 are available at
http://awel.domblogger.net/7/php/

If you are interested in PHP 5.6.x for RHEL / CentOS 7 I suggest you use the
yum repository available at that link rather than using these spec files to
build them yourself, but of course you can use these spec files to build them
yourself if you would prefer.

About
-----

I started with the PHP RPM spec file from Fedora 20 and modified it to build
the 5.6.x branch of PHP in CentOS 7. Most modules that are not built as part of
PHP itself are straight rebuilds of source RPMs available either in CentOS 7 or
EPEL for CentOS 7 or Fedora 20.

Rebuilding is necessary as PHP 5.6.x has a different binary API version than
the version of PHP that ships with RHEL / CentOS 7.

ImageMagick was rebuilt and updated to provide WebP support so that the binary
PHP module of ImageMagick could be used to generate WebP images within PHP.

libxml2 was updated, the update is an upstream patch release and is binary
compatible with the version of libxml2 that ships with RHEL / CentOS 7.

libxml2 is very important to my personal PHP needs which is why I prefer to
keep current with upstream rather than just backport security fixes like
RHEL / CentOS do in the distribution libxml2.

Other than pear itself, pear modules are not packages. Pear modules are not
binary, and are best managed by the `/usr/bin/pear` utility rather than by RPM.

The purpose of this git is to provide a place where the RPM spec files and/or
patches can be obtained without needing to download the `src.rpm` files.

This is also the best replace to report any problems with the packages that you
may encounter.

Enjoy.
