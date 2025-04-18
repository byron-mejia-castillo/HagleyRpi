# Hagley Museum Guest Tracking System
# Benjamin Page 4/17/2025

This repository contains all developed code for the Raspberry Pi-based guest tracking system created as part of the GMU IT Capstone Project. The system uses a USB camera connected to a Raspberry Pi 5 to monitor foot traffic at museum exhibits and automatically log guest counts to Airtable.

---

## System Components

- Raspberry Pi 5 (8GB model)
- InnoMaker USB Camera Module (U20CAM-720P)
- InnoMaker Aluminum Camera Shell (ASIN: B0CLXV25NR)
- Raspberry Pi OS (Bookworm, 64-bit)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/bp634/HagleyRpi.git
cd HagleyRpi
```

### 2. Configure the System

Edit the config files (if present) or update hardcoded values in:

- `airtable_push.py`: Add your Airtable API credentials and table info
- `tracker_logic.py`: Adjust zone lines or detection parameters if needed

**Note:** The Airtable credentials must be kept secure. Avoid committing your API keys to the public repo.

### 3. Install Dependencies

```bash
sudo apt update
sudo apt install python3-opencv python3-pip ffmpeg libatlas-base-dev
pip3 install -r requirements.txt
```

### 4. Enable the Tracking System at Boot

To run the main system automatically using `systemd`, install and enable the service file (not included in this repo but referenced in documentation):

```bash
sudo cp systemd/guest-tracker.service /etc/systemd/system/
sudo systemctl enable guest-tracker.service
sudo systemctl start guest-tracker.service
```

---

##  Running the System Manually

```bash
cd USB-Scripts
python3 live_tracker.py
```

- The script will wait until 10:00 AM EST to begin tracking.
- People are detected and tracked based on movement across defined zones.
- Every 30 minutes, the system pushes guest count data to Airtable.

---

##  Repository Structure

```
guestcount/
├── USB-Scripts/                # Final tracking system logic and Airtable integration
│   ├── airtable_push.py        # Sends guest count data to Airtable
│   ├── live_tracker.py         # Main runtime script with start-time delay and loop
│   └── tracker_logic.py        # Person detection logic with line-crossing detection
│
├── pi-camera/                  # Early-stage experimental modules for raw capture
│   ├── airtable.py             # Alternate Airtable interface
│   ├── camera.py               # Frame-grabbing test script
│   └── counter.py              # Prototype for early people-counting logic
│
├── README.md                   # This documentation file
```

---

##  Security Notes

- Do not commit API keys or access tokens directly in code.
- Consider using `.env` files or environment variables in production environments.

---

##  Troubleshooting

- **Camera not detected?** Run `ls /dev/video0` 
- **Adjust Camera focus?** Run 'sudo python focus_preview.py'
- **Tracking inaccurate?** Tweak detection zones in `tracker_logic.py`
- **No Airtable updates?** Confirm the API key and Airtable base/table info are correct
- **Script not running?** Confirm status with 'sudo systemctl status guest-tracker.service'


##  License

This project is provided under the MIT License.