## Rundeck Exporter Systemd Unit

---

The systemd unit file for the rundeck_exporter should be installed on **/etc/systemd/system**.

It requires the creation of the user **rundeck_exporter** with **/usr/bin/nologin** as default shell and no privileges associated.

The configuration file with the necessary options and environment variables must be defined in the file **/etc/default/rundeck_exporter**. Any rundeck_exporter params that can be passed as environment variable can be defined in the configuration file. See **rundeck_exporter.default**.

Install the exporter from PyPI and ensure the binary is available at the path referenced in `ExecStart` of the service file:

```sh
pip install rundeck-exporter
which rundeck_exporter  # confirm install path
```
