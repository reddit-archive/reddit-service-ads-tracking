class packages {
  # Add reddit package apt-repo
  exec { 'reddit-repo-add':
    command => 'sudo add-apt-repository ppa:reddit/ppa -y',
    unless  => 'apt-cache policy | grep reddit',
    notify => Exec['update-apt'],
  }

  # Update apt
  exec { 'update-apt':
    command     => 'sudo apt-get update',
    refreshonly => true,
  }

  # Install the dependencies
  package {
    [
      'python',
      'python-setuptools',
      'python3-setuptools',
      'python-dev',
      'python-pip',
      'python-gevent',
      'python3-baseplate',
      'python-baseplate',
      'python-pyramid',
      'einhorn',
      'python-webtest',
      'python3-webtest',
      'python-coverage',
      'python3-coverage',
      'python-nose',
      'python3-nose',
      'python-mock',
      'python3-mock',
      'python-httpagentparser',
      'python-enum34',
    ]:
      ensure  => installed,
      require => [
        Exec['reddit-repo-add'], # add reddit repo for baseplate and einhorn
        Exec['update-apt'],      # The system update needs to run
      ],
  }
}
