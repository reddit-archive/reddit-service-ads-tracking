# Installation of initial dependencies and baseplate application
# for reddit_service_ads_tracking in a development environment.
# Please add additional dependencies and env setup code as needed.

Exec { path => [ '/usr/bin', '/usr/sbin', '/bin', '/usr/local/bin', '/sbin' ] }

class ads-tracking {
  if $::project_path {
    $project_path = $::project_path
  }
  else {
    $project_path = undef
    warning("`project_path` undefined, using current working directory")
  }

  # Set up the app
  exec { 'install-app':
    cwd     => $project_path,
    command => 'make',
    require => [
      Package['python-setuptools'],
      Package['python-baseplate'],
    ],
  }

  # Set up the app
  exec { 'install-app3':
    cwd     => $project_path,
    command => 'make python3',
    require => [
      Package['python3-setuptools'],
      Package['python3-baseplate'],
    ],
  }
}

include packages
include events
include ads-tracking
