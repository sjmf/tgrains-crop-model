# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install vagrant-disksize to allow resizing the vagrant box disk.
unless Vagrant.has_plugin?("vagrant-disksize")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-disksize plugin is missing. Please install it using 'vagrant plugin install vagrant-disksize' and rerun 'vagrant up'"
end

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "centos/8"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Jupyter notebook (development)
  config.vm.network "forwarded_port", guest: 8888, host: 8888, host_ip: "127.0.0.1"

  # Flask (development)
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"

  # Nginx/UWSGI (production)
  config.vm.network "forwarded_port", guest: 80, host: 8000, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/vagrant_data", type: "virtualbox"
  config.vm.synced_folder '.', '/vagrant', disabled: true

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Configure disk size using the plugin vagrant-disksize.
  # This is installed using vagrant plugin install vagrant-disksize
  #
  config.disksize.size = '20GB'

  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # config.vm.provision "shell", inline: <<-SHELL
  #   apt-get update
  #   apt-get install -y apache2
  # SHELL

  config.vm.provision "shell", inline: <<-SHELL
    set -e
    #script_name=`basename $0`
    #script_relative_path=`dirname $0`
    #cp "$script_relative_path/$script_name" $HOME

    BORDER="===================================================="

    echo $BORDER
    echo "Installing binutils..."

    # Get GCC compiler, etc
    yum -y update
    yum -y groupinstall "Development Tools"
    yum -y install wget

    echo $BORDER
    echo "Installing miniconda..."

    # Provisioner runs as root. Sudo as `vagrant` user:
    # Devtoolset on Centos6 breaks sudo with a wrapper. Call /usr/bin/sudo directly
    /usr/bin/sudo -i -u vagrant bash <<"EOF"
        if [[ ! -d "$HOME/miniconda" ]];
        then
            # Install miniconda
            wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
            bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda
            rm Miniconda3-latest-Linux-x86_64.sh

#            echo "Modifying PATH..."
#            sed -i 's;^PATH=\(.*\);PATH=\1\:\$HOME\/miniconda\/bin;' $HOME/.bash_profile
#            grep "PATH" -n .bash_profile
        else
            echo "Miniconda already installed! ^_^"
        fi
EOF


    echo $BORDER
    echo "Installing cppyy and development tools using conda..."

    /usr/bin/sudo -i -u vagrant bash <<"EOF"
        if [[ -d "$HOME/miniconda" ]];
        then
            PATH="$PATH:$HOME/miniconda/bin"
            conda init bash
            eval "$(conda shell.bash hook)"
            conda update -y -n base -c defaults conda
            # We originally configured a conda environment here, but leaving it as (base) solves problems!
            conda install -yc conda-forge cppyy
            conda install -y flask markdown

            # Development tools
            conda install -yc conda-forge jupyter
            jupyter notebook --generate-config
            sed -i 's/c.NotebookApp.ip.*/c.NotebookApp.ip = "0.0.0.0"/g' /home/vagrant/.jupyter/jupyter_notebook_config.py

            conda install xeus xeus-cling -c conda-forge
            conda install jupyterthemes -c conda-forge
            jt -t monokai
        else
            echo "Miniconda not installed!"
            exit 1
        fi
EOF

    # Docker install (as root)
    /usr/bin/sudo -i bash <<"EOF"
        dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
        dnf install -y https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.6-3.3.el7.x86_64.rpm
        dnf install -y docker-ce
        systemctl enable docker
        systemctl disable firewalld

        curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o docker-compose
        mv docker-compose /usr/local/bin
        chmod +x /usr/local/bin/docker-compose

        usermod -a -G docker vagrant
EOF

    echo $BORDER
    echo "To install VirtualBox Guest Additions for 2-way synced folder, manual"
    echo "steps are required as you need to mount the ISO: See"
    echo "https://www.if-not-true-then-false.com/2010/install-virtualbox-guest-additions-on-fedora-centos-red-hat-rhel/"
    # Guest additions instructions for mount folder in 2-way synced_folder
    echo -e "\n"
    echo <<"EOF"
        sudo -i
        yum update kernel*
        dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
        yum install -y gcc kernel-devel kernel-headers dkms make bzip2 perl

        KERN_DIR=/usr/src/kernels/`uname -r`
        export KERN_DIR

        mkdir /media/VirtualBoxGuestAdditions
        mount -r /dev/cdrom /media/VirtualBoxGuestAdditions
        cd /media/VirtualBoxGuestAdditions

        ./VBoxLinuxAdditions.run
        reboot
EOF
  SHELL
end

  #NB: In configuring the interpreter in PyCharm, specify the interpreter as /home/vagrant/miniconda/bin/python
  #    It will fail silently if it can't find the executable (e.g. if it's set to the default /usr/bin/python)
