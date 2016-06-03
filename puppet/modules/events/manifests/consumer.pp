define events::consumer (
  $queue = $title,
  $user = $::user,
) {
  file { "/etc/init/events-discard-${queue}.conf":
    ensure  => file,
    content => template('events/discard-consumer.upstart.erb'),
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
  }

  service { "events-discard-${queue}":
    ensure  => running,
    require => File["/etc/init/events-discard-${queue}.conf"],
  }
}
