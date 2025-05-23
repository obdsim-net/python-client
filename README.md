```markdown
# client-py

A lightweight Python client that bridges TCP and CAN interfaces for OBD-II simulation via [obdsim.net](https://obdsim.net).

This client connects to a remote OBD-II simulation server and forwards traffic between a local CAN interface (e.g., `vcan0`) and the simulator backend over TCP.

---

## Features

- ✅ Connects to `obdsim.net` TCP simulator  
- 🔁 Forwards CAN frames bidirectionally (CAN ↔ TCP)  
- 🔌 Supports `socketcan` interfaces (`vcan0`, `can0`, etc.)  
- 📦 Easy installation via `pip`

---

## Installation

```bash
pip install git+https://github.com/your-org/client-py.git
```

Or clone and install locally:

```bash
git clone https://github.com/your-org/client-py.git
cd client-py
pip install .
```

---

## Usage

```bash
python3 -m client \
  --config <your-config-id> \
  --host port.obdsim.net \
  --port 1337 \
  --channel vcan0
```

### Parameters

| Flag        | Description                        | Default           |
|-------------|------------------------------------|-------------------|
| `--config`  | Your simulator config ID           | (required)        |
| `--host`    | Hostname of the TCP simulator       | `port.obdsim.net` |
| `--port`    | TCP port to connect to              | `1337`            |
| `--channel` | CAN interface name (e.g. `vcan0`)   | `vcan0`           |

---

## Example

Assuming `vcan0` is set up and your config ID is `abc123`:

```bash
python3 -m client --config abc123 --channel vcan0
```

---

## Troubleshooting

- 🔌 Make sure `vcan0` is created:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

- ❌ If the config is not found, the client will exit with an error.

---

## License

MIT © obdsim.net contributors
```
