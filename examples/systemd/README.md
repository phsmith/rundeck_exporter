## Rundeck Exporter Systemd Unit
---

The systemd unit file for the rundeck_exporter should be installed on **/etc/systemd/system**.

It requires the creation of the user **rundeck_exporter** with **/usr/bin/nologin** as default shell and no privileges associated.

The configuration file with the necessary options and environment variables must be defined in the file **/etc/default/rundeck_exporter**. Any rundeck_exporter params that can be passed as environment variable can be defined in the configuration file. See **rundeck_exporter.default**.

The file **rundeck_exporter.py** must be copied to **/usr/bin/rundeck_exporter**, without the .py, or can be copied to any other location but the ExecStart on rundeck_exporter.service must be modified.
