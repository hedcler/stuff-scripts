#!/usr/bin/env python
# coding: utf-8
#
# @desc Easy RPM
# @author Thiago Ribeiro <ribeiro dot it at gmail dot com>
#
# @usage:
# cd [PATH_OF_FILES]
# find . -iname "*" -not -path "*/\.*" -not -name "*pyc" -printf '%P\n' > /tmp/my_app_files
# git log --format='* %ai - %cn <%ce>%n-%h - %s%n' --first-parent > /tmp/my_app_changelog
# cd -
# ./easy-rpm.py --name "my-app" --version 1.1.0 --release 2 --desc "My Example Application" \
# --url "http://myapp.com" --rpmgroup "My Applications" --sfiles /tmp/my_app_files \
# --dfiles "/opt/myapp" --user myapp_user --changelog /tmp/my_app_changelog > /tmp/MY_APP_SPEC
#
import os
import re
import optparse

DIR = os.path.dirname(os.path.realpath(__file__))
SPEC = """
Name:           ##APP_NAME##
Version:        ##APP_VERSION##
Release:        ##APP_RELEASE##%{?dist}
Summary:        ##APP_DESCRIPTION##

Group:          ##APP_GROUP_RPM##
License:        ##APP_LICENSE##
URL:            ##APP_URL##
Source0:        ##APP_NAME##-%{version}.tar.gz
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


#BuildRequires:
Requires(pre): /usr/sbin/useradd, /usr/bin/getent
Requires(postrun): /usr/sbin/userdel

%description
##APP_COMPLETE_DESCRIPTION##

%prep
%define _unpackaged_files_terminate_build 0

%setup -q

%build

%pre
/usr/bin/getent group ##APP_USER## || /usr/sbin/groupadd -r ##APP_USER##
/usr/bin/getent passwd ##APP_USER## || /usr/sbin/useradd -r -d $RPM_BUILD_ROOT -s /sbin/nologin ##APP_USER##

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/##APP_BUILD_ROOT##/%{name}
##APP_FILES_INSTALL_LIST##

%clean
rm -rf $RPM_BUILD_ROOT

%files
%dir /##APP_BUILD_ROOT##/%{name}
%defattr(-,##APP_USER##,##APP_USER##,-)
##APP_FILES##

%post
chmod 755 -R /##APP_BUILD_ROOT##/%{name}

%changelog
##APP_CHANGELOG##"""

parser = optparse.OptionParser()
parser.add_option('--name', '--NAME', help='Name', dest='name', action='store', default='')
parser.add_option('--version', '--VERSION', help='Version', dest='version', action='store', default='1.0')
parser.add_option('--user', '--USER', help='User to run application', dest='user', action='store', default='nobody')
parser.add_option('--changelog', '--CHANGELOG', help='Application changelog file', dest='changelog', action='store', default='')
parser.add_option('--release', '--RELEASE', help='Release', dest='release', action='store', default='1')
parser.add_option('--desc', '--DESCRIPTION', help='Brief description', dest='desc', action='store', default='')
parser.add_option('--cdesc', '--COMPLETE_DESCRIPTION', help='Complete description', dest='cdesc', action='store', default='')
parser.add_option('--url', '--URL', help='Application URL', dest='url', action='store', default='http://')
parser.add_option('--license', '--LICENSE', help='License', dest='license', action='store', default='GPLv2')
parser.add_option('--rpmgroup', '--RPM_GROUP', help='RPM Group', dest='rpmgroup', action='store', default='Utilities')
parser.add_option('--sfiles', '--SOURCE_FILES', help='Source files', dest='rpmfiles', action='store', default='')
parser.add_option('--dfiles', '--DESTINATION_FILES', help='Destination to files be installed', dest='buildroot', action='store', default='opt')

nt = 0
options = ['name',  'version', 'user', 'changelog', 'release', 'desc', 'cdesc', 'url', 'license', 'rpmgroup', 'rpmfiles']

(opts, args) = parser.parse_args()

for o in options:
    if not opts.__dict__[o]:
        nt += 1
    if len(options) == nt:
        parser.print_help()
        exit(-1)

rpmfiles, filelist = '', ''

if opts.buildroot.startswith('/'):
    opts.buildroot = opts.buildroot[1:]

if opts.rpmfiles != '':
    with open(opts.rpmfiles, 'r') as rf:
        for rl in rf.readlines():
            frl = rl.strip()
            frl = re.sub(r'^%s-%s\/' % (opts.name, opts.version), '', frl)

            if len(frl)>1:
                fdir = re.search(r'(.*)(\/)$', frl, re.M|re.I)
                if fdir:
                    rpmfiles += "install -d %s $RPM_BUILD_ROOT/%s/%s/%s\n" % (frl, opts.buildroot, opts.name, frl)
                else:
                    filelist += "/%s/%s/%s\n" % (opts.buildroot, opts.name, frl)
                    rpmfiles += "install %s $RPM_BUILD_ROOT/%s/%s/%s\n" % (frl, opts.buildroot, opts.name, frl)

if opts.cdesc == '':
    opts.cdesc = opts.desc

if opts.changelog is not '':
    with open(opts.changelog, "r") as _chlog:
        chlog = _chlog.read()
        
_file = (SPEC.replace('##APP_NAME##', opts.name)
             .replace('##APP_VERSION##', opts.version)
             .replace('##APP_USER##', opts.user)
             .replace('##APP_CHANGELOG##', chlog)
             .replace('##APP_RELEASE##', opts.release)
             .replace('##APP_DESCRIPTION##', opts.desc)
             .replace('##APP_COMPLETE_DESCRIPTION##', opts.cdesc)
             .replace('##APP_URL##', opts.url)
             .replace('##APP_LICENSE##', opts.license)
             .replace('##APP_FILES_INSTALL_LIST##', rpmfiles)
             .replace('##APP_FILES##', filelist)
             .replace('##APP_BUILD_ROOT##', opts.buildroot)
             .replace('##APP_GROUP_RPM##', opts.rpmgroup))
print _file
