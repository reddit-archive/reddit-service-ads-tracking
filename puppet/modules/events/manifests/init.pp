class events {
  file { '/etc/sysctl.d/60-message-queues.conf':
    ensure => file,
    source => 'puppet:///modules/events/sysctl',
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
    notify => Exec['reload sysctls'],
  }

  exec { 'reload sysctls':
    command     => '/sbin/sysctl --system',
    refreshonly => true,
  }

  file { '/etc/security/limits.d/message-queues.conf':
    ensure => file,
    source => 'puppet:///modules/events/limits.conf',
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }

  events::consumer { 'production':
    require => [
      Exec['reload sysctls'],
      Package['python-baseplate'],
    ],
  }

}
