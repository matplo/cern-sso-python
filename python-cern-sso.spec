%global sum Cern Single-Single-Sign-On driver
%global srcname cern-sso
%define name python-%{srcname}

Name: python-cern-sso
Version: 1.3.2
Summary:        %{sum}
Release: 2%{?dist}
Source0: %{name}-%{version}.tar.gz
License: MIT
Group: CERN/Utilities
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
BuildRequires: python2-devel python34-devel python-setuptools python34-setuptools
Vendor: Albin Stjerna <albin.stjerna@cern.ch>
Requires: python-requests python-requests-kerberos python-six
Url: https://gitlab.cern.ch/astjerna/cern-sso-python

%description
This is a re-implementation of the Perl script
cern-get-sso-cookie_.
as a Python library. As a bonus, a shell client re-implementing (most
of) the functionality of ``cern-get-sso-cookie``, is also provided.

.. _cern-get-sso-cookie: https://github.com/sashabaranov/cern-get-sso-cookie/

Prerequisites
-------------

This package assumes a working Kerberos and OpenSSL setup, but should be
compatible with both python 2.7 and 3.


Usage
-----

The module provides only two functions: ``krb_sign_on`` and
``cert_sign_on``, used for authentication with Kerberos and certificates
respectively. Both take an optional cookiejar (which can be a Requests
``CookieJar``, or a ``MozillaCookieJar``) which is filled during
operations. In any event, a cookie jar is also returned by both
functions.

The returned cookie jar can be used directly as an argument to Requests'
``cookies``

.. code:: python

          import cern_sso
          import requests

          my_url = "https://my-secret-place.cern.ch"

          cookies = cern_sso.krb_sign_on(my_url)

          # Perform request
          r1 = requests.get(my_url, cookies=cookies)

It is assumed that the user running the program is already authenticated
against Kerberos.


This is what the same procedure would look like using SSL certificates:

.. code:: python

          import cern_sso
          import requests

          my_url = "https://my-secret-place.cern.ch"
          cert_file = "/home/albin/myCert.pem"
          key_file = "/home/albin/myCert.key"

          cookies = cern_sso.cert_sign_on(my_url, cert_file=cert_file,
          key_file=key_file)

          # Perform request
          r1 = requests.get(my_url, cookies=cookies)


Certain limitations apply to the certificate and key files, please see
the following section on command-line usage for further information on
this.

For an example of how to use an external CookieJar, see
``bin/cern-get-sso-cookie.py``.

Using ``cern-get-sso-cookie.py``
------------------------------

Just like ``cern-get-sso-cookie``, the Python implementation will
authenticate against a desired URL and returna Mozilla cookie-file
suitable for use with Curl or Wget.

For use with Kerberos, make sure you are authenticated either via
password or a keytab:

.. code:: sh
          $ kinit me@CERN.CH
          <enter password>


Now you can perform the authentication:

.. code:: sh
          $ cern-get-sso-cookie.py --url https://cerntraining.service-now.com --kerberos
          # cookies.txt now contains the relevant session cookies
          $ curl -L --cookie cookies.txt --cookie-jar cookies.txt -H 'Accept: application/json' "https://cerntraining.service-now.com/api/now/v1/table/incident"


In the spirit of the UNIX philosophy, ``cern-get-sso-cookie.py`` outputs
nothing on success. Please try ``--verbose`` or even ``--debug`` if that is
not to your liking!

For authentication against a SSL certificate (and key), you first need
to process the certificate files to remove passwords and separate the
key and certificate:

.. code:: sh
          $ openssl pkcs12 -clcerts -nokeys -in myCert.p12 -out myCert.pem

          $ openssl pkcs12 -nocerts -in myCert.p12 -out myCert.tmp.key

          $ openssl rsa -in myCert.tmp.key -out myCert.key

It is assumed that your certificate and key files have the same base
name and are located in the same folder, and that the key has the file
ending ``.key`` and the certificate ``.pem``. In the example above, the base
name ``myCert`` was used.

Finally, you can use the certificates to obtain a SSO cookie:

.. code:: sh
          $ cern-get-sso-cookie.py --url https://cerntraining.service-now.com --cert myCert


For further notes on usage, see ``cern-get-sso-cookie.py --help``.

%package -n python2-%{srcname}
Summary:        %{sum}
Requires: python-requests python-requests-kerberos python-six
#%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
An python module which provides a convenient example.


%package -n python3-%{srcname}
Summary:        %{sum}
Requires: python34-requests python34-requests-kerberos python34-six
#%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
An python module which provides a convenient example.


%prep
%setup -q

%build
%{__python3} setup.py build  --executable=%{__python2}
%{__python2} setup.py build  --executable=%{__python2}

%install
%{__rm} -rf %{buildroot}

%{__python3} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --prefix=/usr --record=INSTALLED_FILES_3
%{__python2} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --prefix=/usr --record=INSTALLED_FILES_2

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python2-%{srcname}
%doc README.rst
# %files -f INSTALLED_FILES_2
%{python2_sitelib}/*
%{_bindir}/cern-get-sso-cookie.py
%defattr(-,root,root,-)

%files -n python3-%{srcname}
%doc README.rst
# %files -f INSTALLED_FILES_3
%{python3_sitelib}/*
%defattr(-,root,root)
