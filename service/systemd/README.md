# pyscreen systemd service

```sh
# Create config directory
mkdir /etc/pyscreen
chown root:root /etc/pyscreen
chmod 0700 /etc/pyscreen

# Copy example config
cp example.yml /etc/pyscreen/pyscreen.yml

# Copy service file
cp service/systemd/pyscreen.service /etc/systemd/system/

# Start and enable service
systemctl start pyscreen
systemctl enable pyscreen
```