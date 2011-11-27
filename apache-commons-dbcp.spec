%global base_name       dbcp
%global short_name      commons-%{base_name}

Name:             apache-%{short_name}
Version:          1.4
Release:          8
Summary:          Apache Commons DataBase Pooling Package
Group:            Development/Java
License:          ASL 2.0
URL:              http://commons.apache.org/%{base_name}/
Source0:          http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz

# Depmap needed to remove tomcat* deps (needed only for testing) 
# and fix geronimo transaction
Source1:          %{short_name}.depmap
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:        noarch

BuildRequires:    java-devel >= 0:1.6.0
BuildRequires:    jpackage-utils
BuildRequires:    apache-commons-parent
BuildRequires:    apache-commons-pool
BuildRequires:    geronimo-parent-poms
BuildRequires:    jta
BuildRequires:    maven-plugin-cobertura

Requires:         java >= 0:1.6.0
Requires:         jpackage-utils
Requires:         apache-commons-pool

Requires(post):   jpackage-utils
Requires(postun): jpackage-utils

# This should go away with F-17
Provides:         jakarta-%{short_name} = 0:%{version}-%{release}
Obsoletes:        jakarta-%{short_name} < 0:1.4-1
Obsoletes:        jakarta-%{short_name}-tomcat5 < 0:1.4-1
Obsoletes:        hibernate_jdbc_cache < 0:1.4-1

%description
Many Apache projects support interaction with a relational database. Creating a 
new connection for each user can be time consuming (often requiring multiple 
seconds of clock time), in order to perform a database transaction that might 
take milliseconds. Opening a connection per user can be unfeasible in a 
publicly-hosted Internet application where the number of simultaneous users can 
be very large. Accordingly, developers often wish to share a "pool" of open 
connections between all of the application's current users. The number of users 
actually performing a request at any given time is usually a very small 
percentage of the total number of active users, and during request processing 
is the only time that a database connection is required. The application itself 
logs into the DBMS, and handles any user account issues internally.

%package javadoc
Summary:          Javadoc for %{name}
Group:            Development/Java
Requires:         jpackage-utils
# This should go away with F-17
Obsoletes:        jakarta-%{short_name}-javadoc < 0:1.4-1

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n %{short_name}-%{version}-src
iconv -f iso8859-1 -t utf-8 RELEASE-NOTES.txt > RELEASE-NOTES.txt.conv && mv -f RELEASE-NOTES.txt.conv RELEASE-NOTES.txt

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository

# Skip tests, tomcat:naming-java and tomcat:naming-common not available
mvn-jpp \
        -e \
        -Dmaven2.jpp.mode=true \
        -Dmaven2.jpp.depmap.file="%{SOURCE1}" \
        -Dmaven.test.skip=true \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:javadoc

%install
rm -rf %{buildroot}

# jars
install -d -m 0755 %{buildroot}%{_javadir}
install -pm 644 target/%{short_name}-%{version}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|apache-||g"`; done)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# pom
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{short_name}.pom
%add_to_maven_depmap org.apache.commons %{short_name} %{version} JPP %{short_name}

# following line is only for backwards compatibility. New packages
# should use proper groupid org.apache.commons and also artifactid
%add_to_maven_depmap %{short_name} %{short_name} %{version} JPP %{short_name}

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr target/site/api*/* %{buildroot}%{_javadocdir}/%{name}-%{version}/
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE.txt NOTICE.txt README.txt RELEASE-NOTES.txt
%{_javadir}/*
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

