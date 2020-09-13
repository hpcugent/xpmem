%global buildforkernels newest
%global kmod_name xpmem
%global rversion master

Name:          xpmem-kmod
Version:       2.6.5
# Taken over by kmodtool
# Based on http://springdale.math.ias.edu/data/puias/computational/7/SRPMS/xpmem-kmod-2.6.3-1.sdl7.3.src.rpm
Release:       1%{?dist}.%{gittag}.1.ug
Summary:       Kernel module that enables a process to map the memory of another process
Group:         System Environment/Kernel
License:       Redistributable, no modification permitted
URL:           https://github.com/hjelmn/xpmem
Source:        xpmem-%{version}.tar.gz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

ExclusiveArch:  i686 x86_64

BuildRequires:  autoconf automake libtool systemd
BuildRequires: kernel-rpm-macros
BuildRequires:  %{kernel_module_package_buildreqs}
%kernel_module_package -n %{kmod_name} -p %{SOURCE12}

%description
XPMEM is a Linux kernel module that enables a process to map the memory of
another process into its virtual address space.

%package -n xpmem-lib
Summary:       XPMEM udev rule
Group:         System Environment/Kernel

%description -n xpmem-lib
Just a udev rule for XPMEM.

%package -n xpmem-devel
Summary:       Development files for XPMEM
Group:         Development/Libraries
Requires:      xpmem-lib = %{version}-%{release}

%description -n xpmem-devel
Development files for XPMEM.

%package -n xpmem-static
Summary:       Static library for XPMEM
Group:         Development/Libraries
Requires:      xpmem-devel = %{version}-%{release}

%description -n xpmem-static
Static library for XPMEM.

%prep
%setup -c -n %{name}-%{version}
ls
for flavor in %flavors_to_build ; do
%ifarch %{ix86}
    cp -a %{kmod_name}-%{version} _kmod_build_${flavor}
%else
    cp -a %{kmod_name}-%{version} _kmod_build_${flavor}
%endif
done


%build
for flavor in %flavors_to_build ; do
  pushd _kmod_build_${flavor}
    ./autogen.sh
    %configure --with-kerneldir="%{kernel_source $flavor}" --with-default-prefix=%{_prefix} --with-module=/lib/modules/%kverrel${flavor%default}/extra/xpmem
    make
#    make %{?_smp_mflags} \
#        KERNEL_UNAME="%{kernel_version $flavor}" SYSSRC="%{kernel_source $flavor}" \
#        IGNORE_CC_MISMATCH=1 IGNORE_XEN_PRESENCE=1 IGNORE_PREEMPT_RT_PRESENCE=1 \
#        %{?_nv_build_module_instances:NV_BUILD_MODULE_INSTANCES=%{?_nv_build_module_instances}} \
#       modul
  popd
done

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{%{_libdir},%{_includedir},%{_udevrulesdir}}
for flavor in %flavors_to_build ; do
    pushd _kmod_build_${flavor}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/%kverrel${flavor%default}/extra/xpmem
    install -D -m 0755 kernel/xpmem.ko $RPM_BUILD_ROOT/lib/modules/%kverrel${flavor%default}/extra/xpmem
    if [ ! -e "$RPM_BUILD_ROOT%{_includedir}/xpmem.h" ]; then
	install -m 644 include/xpmem.h $RPM_BUILD_ROOT%{_includedir}
	install -m 644 lib/.libs/libxpmem.a $RPM_BUILD_ROOT%{_libdir}
	cp -a lib/.libs/libxpmem.so* $RPM_BUILD_ROOT%{_libdir}
	install -m 644 56-xpmem.rules $RPM_BUILD_ROOT%{_udevrulesdir}
    fi
    popd
done

%files -n xpmem-lib
%defattr(-,root,root)
%{_libdir}/libxpmem.so.*
%{_udevrulesdir}/*

%files -n xpmem-devel
%defattr(-,root,root)
%{_includedir}/xpmem.h
%{_libdir}/libxpmem.so

%files -n xpmem-static
%defattr(-,root,root)
%{_libdir}/libxpmem.a

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Thu Jan 21 2016 Josko Plazonic <plazonic@princeton.edu>
-  initial release
