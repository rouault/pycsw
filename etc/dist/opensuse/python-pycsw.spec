# =================================================================
#
# Authors: Angelos Tzotsos <tzotsos@opensuse.org>
#
# Copyright (c) 2015 Angelos Tzotsos
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

%define _webappconfdir /etc/apache2/conf.d/
%define _htdocsdir /srv/www/htdocs/

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%define pyname pycsw

Name:           python-%{pyname}
Version:        1.10.0
Release:        1
License:        MIT
Summary:        An OGC CSW server implementation written in Python
Url:            http://pycsw.org/
Group:          Productivity/Scientific/Other
Source0:        %{pyname}-%{version}.tar.gz
Requires:	python
Requires:	python-sqlalchemy
Requires:	python-Shapely
Requires:	python-lxml
Requires:	python-owslib
Requires:	python-pyproj
BuildRequires:  fdupes python 
BuildArch:      noarch
Provides:       %{pyname} = %{version}

BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
pycsw implements clause 10 (HTTP protocol binding (Catalogue Services for the Web, CSW)) 
of the OpenGIS Catalogue Service Implementation Specification, version 2.0.2. 
Initial development started in 2010 (more formally announced in 2011). 
The  project  is  certified  OGC  Compliant,  and  is  an  OGC  Reference  Implementation. 
pycsw allows for the publishing and discovery of geospatial metadata. 
Existing repositories of geospatial metadata can be exposed via OGC:CSW 2.0.2.
pycsw is Open Source, released under an MIT license, and runs on all major platforms (Windows, Linux, Mac OS X)

%package -n %{pyname}-cgi
Summary:        CGI frondend to pycsw using apache web server
Group:          Productivity/Scientific/Other
Requires:       apache2
Requires:       %{pyname} = %{version}
%description -n %{pyname}-cgi
Python CGI frondend to pycsw using apache web server

%prep
%setup -q -n %{pyname}-%{version}

%build

%install
rm -rf %{buildroot}

python setup.py install --prefix=%{_prefix} --root=%{buildroot} \
                                            --record-rpm=INSTALLED_FILES

mkdir -p %{buildroot}/srv/www/htdocs/pycsw
mkdir -p %{buildroot}%{_sysconfdir}/apache2/conf.d

#mv data %{buildroot}/srv/www/htdocs/pycsw/
mv tests %{buildroot}/srv/www/htdocs/pycsw/
mv csw.py %{buildroot}/srv/www/htdocs/pycsw/
mv csw.wsgi %{buildroot}/srv/www/htdocs/pycsw/
mv COMMITTERS.txt %{buildroot}/srv/www/htdocs/pycsw/
mv default-sample.cfg %{buildroot}/srv/www/htdocs/pycsw/
mv HISTORY.txt %{buildroot}/srv/www/htdocs/pycsw/
mv LICENSE.txt %{buildroot}/srv/www/htdocs/pycsw/
mv README.txt %{buildroot}/srv/www/htdocs/pycsw/
mv VERSION.txt %{buildroot}/srv/www/htdocs/pycsw/

cat > %{buildroot}%{_sysconfdir}/apache2/conf.d/pycsw.conf << EOF
<Location /pycsw/>
  Options FollowSymLinks +ExecCGI
  Allow from all
  AddHandler cgi-script .py
</Location>
EOF

cat > %{buildroot}/srv/www/htdocs/pycsw/default.cfg << EOF
[server]
home=/srv/www/htdocs/pycsw
url=http://localhost/pycsw/csw.py
mimetype=application/xml; charset=UTF-8                                                             
encoding=UTF-8
language=en-US
maxrecords=10
#loglevel=DEBUG
#logfile=/tmp/pycsw.log
#ogc_schemas_base=http://foo
#federatedcatalogues=http://geo.data.gov/geoportal/csw/discovery
pretty_print=true
#gzip_compresslevel=8
#domainquerytype=range
#domaincounts=true
profiles=apiso

[manager]
transactions=false
allowed_ips=127.0.0.1
#csw_harvest_pagesize=10

[metadata:main]
identification_title=pycsw Geospatial Catalogue
identification_abstract=pycsw is an OGC CSW server implementation written in Python
identification_keywords=catalogue,discovery,metadata
identification_keywords_type=theme
identification_fees=None
identification_accessconstraints=None
provider_name=Organization Name
provider_url=http://pycsw.org/
contact_name=Lastname, Firstname
contact_position=Position Title
contact_address=Mailing Address
contact_city=City
contact_stateorprovince=Administrative Area
contact_postalcode=Zip or Postal Code
contact_country=Country
contact_phone=+xx-xxx-xxx-xxxx
contact_fax=+xx-xxx-xxx-xxxx
contact_email=Email Address
contact_url=Contact URL
contact_hours=Hours of Service
contact_instructions=During hours of service.  Off on weekends.
contact_role=pointOfContact

[repository]
# sqlite
database=sqlite:////srv/www/htdocs/pycsw/tests/suites/cite/data/records.db
# postgres
#database=postgresql://username:password@localhost/pycsw
# mysql
#database=mysql://username:password@localhost/pycsw?charset=utf8
#mappings=path/to/mappings.py
table=records

[metadata:inspire]
enabled=true
languages_supported=eng,gre
default_language=eng
date=YYYY-MM-DD
gemet_keywords=Utility and governmental services
conformity_service=notEvaluated
contact_name=Organization Name
contact_email=Email Address
temp_extent=2012-09-09/2012-09-10
EOF

%fdupes -s %{buildroot}

%post 
python /srv/www/htdocs/pycsw/tests/gen_html.py > /srv/www/htdocs/pycsw/tests/index.html

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)
%dir %{python_sitelib}/pycsw
%{python_sitelib}/pycsw/

%files -n %{pyname}-cgi
%defattr(-,root,root)
%config(noreplace) %{_webappconfdir}/pycsw.conf
%dir %{_sysconfdir}/apache2/
%dir %{_webappconfdir}/
%dir %{_htdocsdir}/pycsw/
%{_htdocsdir}/pycsw/*

%changelog
